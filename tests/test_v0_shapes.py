"""Pydantic models against v0 payloads that the @hvakr/client Zod schemas accept.

The JSON files in ``tests/fixtures/v0`` come from ``generate_v0_fixtures.cjs``.
That script checks each payload with the matching @hvakr/client schema before
it writes the file.
"""

import json
from pathlib import Path
from typing import Any, get_args

import pytest
from pydantic import BaseModel, ValidationError
from pytest_httpx import HTTPXMock

from hvakr import HVAKRClient
from hvakr.client import _CalculationSection, _ProjectSubcollectionKey
from hvakr.schemas import (
    APIProjectCalculations,
    EquipmentComponentType,
    EquipmentInletMethod,
    GraphNode,
    MetaGraphNode,
    NodeType,
    OutsideAirMethod,
)
from hvakr.schemas.project import ProjectSubcollections

FIXTURES = Path(__file__).parent / "fixtures" / "v0"


def load_fixture(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text())["value"]


def dump(model: BaseModel) -> Any:
    return model.model_dump(mode="json", by_alias=True, exclude_none=True)


def test_fixtures_come_from_the_client_version_the_api_uses() -> None:
    versions = {json.loads(path.read_text())["clientVersion"] for path in FIXTURES.glob("*.json")}
    assert versions == {"0.31.0"}


class TestKeys:
    def test_expand_keys_match_v0_project_subcollection_keys(self) -> None:
        keys = load_fixture("keys.json")
        assert list(get_args(_ProjectSubcollectionKey)) == keys["expandKeys"]

    def test_project_subcollections_model_has_one_field_per_expand_key(self) -> None:
        keys = load_fixture("keys.json")
        wire_names = [
            field.alias or name for name, field in ProjectSubcollections.model_fields.items()
        ]
        assert sorted(wire_names) == sorted(keys["expandKeys"])

    def test_calculation_sections_match_v0_include_enum(self) -> None:
        keys = load_fixture("keys.json")
        assert list(get_args(_CalculationSection)) == keys["calculationSections"]


class TestGraphUnitNodes:
    def test_graph_round_trips_without_dropping_fields(self) -> None:
        graph = load_fixture("graph.json")
        parsed = {node_id: GraphNode.model_validate(node) for node_id, node in graph.items()}
        assert {node_id: dump(node) for node_id, node in parsed.items()} == graph

    def test_central_unit_exposes_equipment_configuration(self) -> None:
        node = GraphNode.model_validate(load_fixture("graph.json")["unit-ahu-1"])

        assert node.node_type is NodeType.CENTRAL_UNIT
        assert node.system_id == "system-1"
        assert node.level == 1
        assert node.point is not None and node.point.x == 120
        assert (node.product_id, node.cost, node.width, node.height) == (
            "product-rtu",
            42000,
            144,
            72,
        )
        assert node.components is not None
        assert [component.type for component in node.components] == [
            EquipmentComponentType.OUTSIDE_AIR_INTAKE,
            EquipmentComponentType.COOLING_COIL,
            EquipmentComponentType.HEATING_COIL,
            EquipmentComponentType.EQUIPMENT_INEFFICIENCY,
        ]
        assert node.component_configs_by_mode is not None
        cooling = node.component_configs_by_mode["cooling_mode"]
        assert cooling["OA"].configuration.method is OutsideAirMethod.PERCENT
        assert cooling["OA"].configuration.percentage == 0.2
        assert cooling["CC"].configuration.target_temperature == 55
        assert cooling["INEFF"].configuration.sensible_heat_gain == {
            "type": "POWER",
            "power": 1500,
        }
        assert node.misc_inefficiencies == 0.01
        assert node.pressure_loss == 0.5
        assert node.outlet is not None
        assert (node.outlet.duct_heat_gain, node.outlet.duct_leakage_percent) == (2, 0.01)
        assert node.energy_configuration is not None
        efficiency = node.energy_configuration.efficiency
        assert efficiency is not None
        assert (
            efficiency.heating_type,
            efficiency.cooling_seer,
            efficiency.heating_cop,
            efficiency.heating_afue,
        ) == ("heatPump", 14, 3.2, 0.8)
        schedule = node.energy_configuration.schedule
        assert schedule is not None and schedule.occupied_hours is not None
        assert len(schedule.occupied_hours) == 24
        assert node.selections is not None
        assert node.selections["heater-1"].product_id == "product-heater"

    def test_unplaced_terminal_unit_has_no_level_or_point(self) -> None:
        node = GraphNode.model_validate(load_fixture("graph.json")["unit-vav-1"])

        assert node.node_type is NodeType.TERMINAL_UNIT
        assert node.zone_id == "zone-1"
        assert node.level is None
        assert node.point is None
        assert node.cost == 0
        assert node.inlet_data is not None
        assert node.inlet_data.configuration.method is EquipmentInletMethod.CUSTOM
        assert node.inlet_data.configuration.flow_rate == 250

    @pytest.mark.parametrize(
        ("node", "message"),
        [
            (
                {
                    "id": "register-1",
                    "adjacencies": [],
                    "nodeType": "REGISTER",
                    "flowType": "SUPPLY",
                    "placementType": "CEILING",
                },
                "REGISTER nodes need level and point",
            ),
            (
                {
                    "id": "unit-1",
                    "adjacencies": [],
                    "nodeType": "CENTRAL_UNIT",
                    "systemId": "system-1",
                    "level": 1,
                },
                "level and point must both be set or both be omitted",
            ),
            (
                {
                    "id": "unit-1",
                    "adjacencies": [],
                    "nodeType": "TERMINAL_UNIT",
                    "zoneId": "zone-1",
                    "cost": -1,
                },
                "greater than or equal to 0",
            ),
        ],
    )
    def test_rejects_nodes_the_v0_schema_rejects(self, node: Any, message: str) -> None:
        with pytest.raises(ValidationError, match=message):
            GraphNode.model_validate(node)


class TestCalculations:
    def test_equipment_results_carry_their_served_scope(self) -> None:
        calculations = APIProjectCalculations.model_validate(load_fixture("calculations.json"))

        assert calculations.equipment is not None
        central = calculations.equipment["unit-ahu-1"]
        assert (central.scope.type, central.scope.id) == ("system", "system-1")
        assert central.modes is not None
        assert central.modes["cooling_mode"]["summary"]["systemProcess"]["total"] == 1500
        terminal = calculations.equipment["unit-vav-1"]
        assert (terminal.scope.type, terminal.scope.id) == ("zone", "zone-1")

    def test_equipment_results_require_scope(self) -> None:
        with pytest.raises(ValidationError, match="scope"):
            APIProjectCalculations.model_validate(
                {"errors": [], "flags": {}, "equipment": {"unit-1": {"modes": {}}}}
            )

    def test_graph_section_keeps_unit_nodes_and_pressures(self) -> None:
        payload = load_fixture("calculations.json")
        calculations = APIProjectCalculations.model_validate(payload)

        assert calculations.graph is not None
        central = calculations.graph["unit-ahu-1"]
        assert central.pressure == 1.2
        assert central.outlet is not None and central.outlet.duct_heat_gain == 2
        assert calculations.graph["unit-vav-1"].level is None
        assert {node_id: dump(node) for node_id, node in calculations.graph.items()} == payload[
            "graph"
        ]

    def test_graph_section_rejects_unplaced_non_unit_nodes(self) -> None:
        with pytest.raises(ValidationError, match="FITTING nodes need level and point"):
            MetaGraphNode.model_validate(
                {"id": "fitting-1", "adjacencies": [], "nodeType": "FITTING"}
            )


class TestSubcollections:
    def test_annotations_exports_and_sheet_file_pages_round_trip(self) -> None:
        payload = load_fixture("subcollections.json")
        subcollections = ProjectSubcollections.model_validate(payload)

        assert subcollections.annotations is not None
        assert subcollections.annotations["annotation-1"].shape == "cloud"
        assert subcollections.exports is not None
        assert subcollections.exports["export-1"].study_name == "Option B"
        assert subcollections.sheet_file_pages is not None
        assert subcollections.sheet_file_pages["page-1"].scale == 48
        assert subcollections.systems is not None
        assert subcollections.systems["system-1"].name == "AHU-1"
        assert dump(subcollections) == payload


class TestClientParsing:
    def test_get_project_parses_unit_nodes_from_expanded_graph(self, httpx_mock: HTTPXMock) -> None:
        graph = load_fixture("graph.json")
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123?expand=graph%2Cexports",
            json={
                "id": "project-123",
                "name": "Test Project",
                "users": {"user-1": {"role": 10}},
                "equipmentModes": {},
                "graph": graph,
                "exports": {},
            },
        )

        with HVAKRClient(access_token="test-token") as client:
            project = client.get_project("project-123", ["graph", "exports"])

        assert project.graph is not None
        assert project.graph["unit-ahu-1"].energy_configuration is not None
        assert project.graph["unit-vav-1"].point is None
        assert project.exports == {}

    def test_get_project_calculations_requests_the_graph_section(
        self, httpx_mock: HTTPXMock
    ) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123/calculations?include=graph%2Cequipment",
            json=load_fixture("calculations.json"),
        )

        with HVAKRClient(access_token="test-token") as client:
            calculations = client.get_project_calculations(
                "project-123", include=["graph", "equipment"]
            )

        assert calculations.graph is not None
        assert calculations.equipment is not None
        assert calculations.equipment["unit-ahu-1"].scope.type == "system"
