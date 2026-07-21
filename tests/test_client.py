"""Tests for the HVAKR v1.0 client surface."""

import pytest
from pydantic import ValidationError
from pytest_httpx import HTTPXMock

from hvakr import APIProjectCalculations, AsyncHVAKRClient, HVAKRClient, HVAKRClientError, Project
from hvakr.schemas import (
    APIJob,
    EquipmentInletMethod,
    EquipmentMode,
    LoadCondition,
    SpaceData,
    TerminalUnitConfiguration,
)

DEFAULT_EQUIPMENT_MODES = {
    "cooling_mode": {
        "id": "cooling_mode",
        "loadCondition": "COOLING",
        "name": "Cooling",
        "description": "",
    },
    "heating_mode": {
        "id": "heating_mode",
        "loadCondition": "HEATING",
        "name": "Heating",
        "description": "",
    },
}

PROJECT_USERS_BY_UID = {
    "firebase-uid-123": {
        "email": "member@example.com",
        "role": 10,
        "firstName": "Member",
        "lastName": "Example",
    }
}


class TestHVAKRClient:
    """Tests for the synchronous client."""

    def test_create_url_encodes_query_values_and_flags(self) -> None:
        client = HVAKRClient(access_token="test-token")
        url = client._create_url(
            "/projects/project id", {"search": "A & B", "expand": True, "unused": False}
        )
        assert url == "https://api.hvakr.com/v0/projects/project id?search=A%20%26%20B&expand"

    def test_auth_headers_identify_the_sdk(self) -> None:
        client = HVAKRClient(access_token="my-secret-token")
        assert client._get_auth_headers() == {
            "Authorization": "Bearer my-secret-token",
            "X-HVAKR-Client": "hvakr-python/1.0.0",
        }

    def test_list_projects_is_paginated_and_filterable(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url=(
                "https://api.hvakr.com/v0/projects?limit=25&cursor=next&search=office"
                "&status=inProgress&projectType=commercial"
            ),
            json={
                "projects": [
                    {
                        "id": "project-1",
                        "name": "Office",
                        "status": "inProgress",
                        "users": PROJECT_USERS_BY_UID,
                    }
                ],
                "hasMore": True,
                "nextCursor": "again",
            },
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.list_projects(
                limit=25,
                cursor="next",
                search="office",
                status="inProgress",
                project_type="commercial",
            )

        assert result.projects[0].id == "project-1"
        assert result.projects[0].users["firebase-uid-123"].email == "member@example.com"
        assert result.has_more is True
        assert result.next_cursor == "again"

    def test_get_project_uses_mode_keyed_project_data(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123",
            json={
                "id": "project-123",
                "name": "Test Project",
                "users": PROJECT_USERS_BY_UID,
                "equipmentModes": DEFAULT_EQUIPMENT_MODES,
            },
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.get_project("project-123")

        assert isinstance(result, Project)
        assert result.equipment_modes["cooling_mode"].load_condition is LoadCondition.COOLING
        assert set(result.users) == {"firebase-uid-123"}
        assert result.users["firebase-uid-123"].email == "member@example.com"

    def test_get_project_can_expand_selected_subcollections(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123?expand=spaces%2Czones",
            json={
                "id": "project-123",
                "name": "Test Project",
                "users": PROJECT_USERS_BY_UID,
                "equipmentModes": DEFAULT_EQUIPMENT_MODES,
                "spaces": {},
                "zones": {},
            },
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.get_project("project-123", ["spaces", "zones"])

        assert result.spaces == {}
        assert result.zones == {}

    def test_write_requests_send_idempotency_key(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(url="https://api.hvakr.com/v0/projects", json={"id": "new-project"})

        with HVAKRClient(access_token="test-token") as client:
            result = client.create_project({"name": "New Project"}, idempotency_key="create-1")

        request = httpx_mock.get_requests()[0]
        assert result == {"id": "new-project"}
        assert request.headers["Idempotency-Key"] == "create-1"
        assert request.headers["X-HVAKR-Client"] == "hvakr-python/1.0.0"

    def test_get_project_calculations_selects_sections(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123/calculations?include=airflows%2Cequipment",
            json={"errors": [], "flags": {}, "equipment": {"system-1": {"modes": {}}}},
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.get_project_calculations(
                "project-123", include=["airflows", "equipment"]
            )

        assert isinstance(result, APIProjectCalculations)
        assert result.equipment == {"system-1": {"modes": {}}}

    def test_job_product_and_me_endpoints(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123/jobs",
            json={"jobId": "job-1", "type": "check", "status": "completed", "result": {}},
        )
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/products?search=fan&limit=10",
            json={
                "products": [{"id": "fan-1", "name": "Fan"}],
                "hasMore": False,
                "nextCursor": None,
            },
        )
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/me",
            json={
                "user": {"id": "user-1", "email": "user@example.com", "license": "team"},
                "organizations": [],
                "plan": {"license": "team", "apiAccess": True},
                "rateLimit": {"limitPerMinute": 60},
            },
        )

        with HVAKRClient(access_token="test-token") as client:
            job = client.create_job("project-123", {"type": "check"})
            products = client.list_products(search="fan", limit=10)
            me = client.me()

        assert isinstance(job, APIJob)
        assert job.job_id == "job-1"
        assert products.products[0].id == "fan-1"
        assert me.rate_limit.limit_per_minute == 60

    def test_error_response_exposes_status_and_metadata(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects",
            status_code=401,
            json={"error": "Unauthorized", "message": "Invalid token"},
        )

        with HVAKRClient(access_token="bad-token") as client:
            with pytest.raises(HVAKRClientError) as exc_info:
                client.list_projects()

        assert exc_info.value.status_code == 401
        assert exc_info.value.status == 401
        assert exc_info.value.metadata == {"error": "Unauthorized", "message": "Invalid token"}


class TestAsyncHVAKRClient:
    """Tests for the asynchronous client."""

    @pytest.mark.asyncio
    async def test_list_projects_and_calculations(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects",
            json={"projects": [], "hasMore": False, "nextCursor": None},
        )
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123/calculations",
            json={"errors": [], "flags": {}},
        )

        async with AsyncHVAKRClient(access_token="test-token") as client:
            projects = await client.list_projects()
            calculations = await client.get_project_calculations("project-123")

        assert projects.projects == []
        assert calculations.errors == []


class TestSchemaValidation:
    """Tests for the modular-equipment data model."""

    def test_project_users_require_email_and_are_indexed_by_uid(self) -> None:
        project = Project.model_validate(
            {
                "id": "project-123",
                "name": "Test Project",
                "users": PROJECT_USERS_BY_UID,
                "equipmentModes": DEFAULT_EQUIPMENT_MODES,
            }
        )

        firebase_uid, member = next(iter(project.users.items()))
        assert firebase_uid == "firebase-uid-123"
        assert member.email == "member@example.com"

    def test_project_users_preserve_pending_sign_up(self) -> None:
        project = Project.model_validate(
            {
                "id": "project-123",
                "name": "Test Project",
                "users": {
                    "firebase-uid-invitee": {
                        "email": "invitee@example.com",
                        "role": 1,
                        "pendingSignUp": True,
                    }
                },
                "equipmentModes": DEFAULT_EQUIPMENT_MODES,
            }
        )

        assert project.users["firebase-uid-invitee"].pending_sign_up is True

    def test_project_rejects_the_previous_email_keyed_membership_shape(self) -> None:
        with pytest.raises(ValidationError, match="email"):
            Project.model_validate(
                {
                    "id": "project-123",
                    "name": "Test Project",
                    "users": {"member@example.com": {"role": 10}},
                    "equipmentModes": DEFAULT_EQUIPMENT_MODES,
                }
            )

    def test_calculations_preserve_airflows_by_project_mode(self) -> None:
        airflow_totals = {
            "supply": 400,
            "return": 300,
            "outside": 100,
            "relief": 0,
            "exhaust": 0,
        }
        mode_airflows = {
            "airflowDifferential": {"design": 0, "required": 0},
            "design": airflow_totals,
            "required": airflow_totals,
            "spacePeaksSum": airflow_totals,
            "supplySources": {
                "codeRequiredSupply": 0,
                "directAirSpaceSensible": 0,
                "directOutsideAir": 0,
                "loadRequiredSupply": 400,
                "totalSpaceSensible": 0,
            },
        }
        calculations = APIProjectCalculations.model_validate(
            {
                "errors": [],
                "flags": {},
                "airflows": {
                    "project": {
                        "byMode": {"cooling_mode": mode_airflows},
                        "calculatedOutsideAirflow": {"cooling": 100, "heating": 0, "max": 100},
                        "max": {
                            "airflowDifferential": {"design": 20, "required": 10},
                            "design": airflow_totals,
                            "required": airflow_totals,
                        },
                        "requiredOutsideAirflowComponents": {
                            "code": {"ach": 0},
                            "load": {"area": 0, "people": 0, "total": 0},
                        },
                    },
                    "spaces": {},
                    "systems": {},
                    "zones": {},
                },
            }
        )

        cooling = calculations.airflows.project.by_mode["cooling_mode"]
        assert cooling.design.supply == 400
        assert calculations.airflows.project.max.required.outside == 100
        assert calculations.airflows.project.max.airflow_differential == {
            "design": 20,
            "required": 10,
        }

    def test_calculations_accept_sidewall_register_schedule_rows(self) -> None:
        calculations = APIProjectCalculations.model_validate(
            {
                "errors": [],
                "flags": {},
                "registerSchedule": [
                    {
                        "configuration": "Supply",
                        "flowType": "SUPPLY",
                        "inletSize": "6 in.",
                        "manufacturer": "Example Manufacturer",
                        "model": "Example Model",
                        "modelType": "sidewall",
                        "quantity": 1,
                        "registerCFM": 100,
                        "registerFPM": 500,
                        "registerNC": 20,
                        "registerSize": "12 x 4 in.",
                        "spaceName": "Office",
                        "spaceNumber": "101",
                        "totalCFM": 100,
                    }
                ],
            }
        )

        assert calculations.register_schedule is not None
        assert calculations.register_schedule[0].model_type.value == "sidewall"

    def test_equipment_mode_and_terminal_config_round_trip(self) -> None:
        mode = EquipmentMode(
            id="cooling_mode",
            loadCondition="COOLING",
            name="Cooling",
            description="",
        )
        config = TerminalUnitConfiguration.model_validate(
            {
                "components": [{"id": "coil", "type": "COOLING_COIL"}],
                "componentConfigsByMode": {
                    "cooling_mode": {
                        "coil": {
                            "enabled": True,
                            "configuration": {
                                "componentType": "COOLING_COIL",
                                "targetTemperature": 55,
                            },
                        }
                    }
                },
            }
        )

        assert mode.load_condition is LoadCondition.COOLING
        component = config.component_configs_by_mode["cooling_mode"]["coil"]
        assert component.configuration.target_temperature == 55

    def test_equipment_inlet_custom_method_uses_inlet_enum(self) -> None:
        config = TerminalUnitConfiguration.model_validate(
            {
                "inletData": {
                    "enabled": True,
                    "configuration": {
                        "componentType": "EQUIPMENT_INLET",
                        "method": "CUSTOM",
                    },
                }
            }
        )

        assert config.inlet_data.configuration.method is EquipmentInletMethod.CUSTOM

    def test_space_uses_per_mode_airflows_and_per_condition_requirements(self) -> None:
        space = SpaceData.model_validate(
            {
                "creationSource": "API",
                "edges": {},
                "level": 1,
                "designAirflowsByMode": {"cooling_mode": {"supplyAir": 400}},
                "airflowRequirementsByLoadCondition": {
                    "COOLING": {"ventilationReq": 100, "infiltrationReqMethod": "AREA"}
                },
            }
        )

        assert space.design_airflows_by_mode["cooling_mode"].supply_air == 400
        cooling_requirements = space.airflow_requirements_by_load_condition[LoadCondition.COOLING]
        assert cooling_requirements.ventilation_req == 100
