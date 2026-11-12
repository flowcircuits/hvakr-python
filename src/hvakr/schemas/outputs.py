"""Output schema definitions for API responses."""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from hvakr.schemas.equipment import EquipmentProjectScope
from hvakr.schemas.graph import DuctSize, FlowType, NodeData


class RegisterModelType(str, Enum):
    """Register model type."""

    CEILING_SQUARE = "ceilingSquare"
    CEILING_LINEAR = "ceilingLinear"
    SIDEWALL = "sidewall"


class ErrorInfo(BaseModel):
    """Error information from API."""

    name: str
    message: str
    stack: str | None = None
    cause: Any | None = None


# Loads schemas
HourlyLoads = list[float]
MonthlyLoads = list[HourlyLoads]


class RoofLoads(BaseModel):
    """Roof load data split by location."""

    ceiling_plenum: MonthlyLoads = Field(alias="ceilingPlenum")
    space: MonthlyLoads

    model_config = {"populate_by_name": True}


class WallLoads(BaseModel):
    """Wall load data split by location."""

    ceiling_plenum: MonthlyLoads = Field(alias="ceilingPlenum")
    space: MonthlyLoads

    model_config = {"populate_by_name": True}


class ExternalCoolingLoads(BaseModel):
    """External cooling load components."""

    doors: MonthlyLoads
    roof: RoofLoads
    skylights: MonthlyLoads
    slab: MonthlyLoads
    walls: WallLoads
    windows: MonthlyLoads


class LatentSensibleInfiltration(BaseModel):
    """Infiltration load components by source."""

    doors: MonthlyLoads
    general: MonthlyLoads
    windows: MonthlyLoads


class InfiltrationCoolingLoads(BaseModel):
    """Infiltration cooling loads."""

    latent: LatentSensibleInfiltration
    sensible: LatentSensibleInfiltration


class LightingLoads(BaseModel):
    """Lighting load data split by location."""

    ceiling_plenum: HourlyLoads = Field(alias="ceilingPlenum")
    space: HourlyLoads

    model_config = {"populate_by_name": True}


class LatentSensibleHourly(BaseModel):
    """Latent and sensible hourly loads."""

    latent: HourlyLoads
    sensible: HourlyLoads


class InternalCoolingLoads(BaseModel):
    """Internal cooling load components."""

    equipment: HourlyLoads
    lighting: LightingLoads
    misc: LatentSensibleHourly
    people: LatentSensibleHourly


class LatentSensibleMonthly(BaseModel):
    """Latent and sensible monthly loads."""

    latent: MonthlyLoads
    sensible: MonthlyLoads


class CoolingLoads(BaseModel):
    """Complete cooling loads breakdown."""

    external: ExternalCoolingLoads
    infiltration: InfiltrationCoolingLoads
    internal: InternalCoolingLoads
    ventilation: LatentSensibleMonthly


class ExternalHeatingLoads(BaseModel):
    """External heating load components."""

    doors: float
    roof: float
    skylights: float
    slab: float
    total: float
    walls: float
    windows: float


class InfiltrationSensibleHeating(BaseModel):
    """Sensible infiltration heating components."""

    doors: float
    general: float
    total: float
    windows: float


class InfiltrationHeatingLoads(BaseModel):
    """Infiltration heating loads."""

    sensible: InfiltrationSensibleHeating
    total: float


class InternalHeatingLoads(BaseModel):
    """Internal heating load components."""

    misc: float
    total: float


class VentilationHeatingLoads(BaseModel):
    """Ventilation heating loads."""

    sensible: float
    total: float


class HeatingLoads(BaseModel):
    """Complete heating loads breakdown."""

    external: ExternalHeatingLoads
    infiltration: InfiltrationHeatingLoads
    internal: InternalHeatingLoads
    total: float
    ventilation: VentilationHeatingLoads


class APIProjectOutputLoads(BaseModel):
    """API response for project loads output."""

    errors: list[ErrorInfo]
    space_cooling_loads: dict[str, CoolingLoads] = Field(alias="spaceCoolingLoads")
    space_heating_loads: dict[str, HeatingLoads] = Field(alias="spaceHeatingLoads")
    system_cooling_loads: dict[str, CoolingLoads] = Field(alias="systemCoolingLoads")
    system_heating_loads: dict[str, HeatingLoads] = Field(alias="systemHeatingLoads")
    zone_cooling_loads: dict[str, CoolingLoads] = Field(alias="zoneCoolingLoads")
    zone_heating_loads: dict[str, HeatingLoads] = Field(alias="zoneHeatingLoads")

    model_config = {"populate_by_name": True}


# Register schedule schemas
class SpaceRegisterScheduleRow(BaseModel):
    """A row in the register schedule."""

    configuration: str
    flow_type: FlowType = Field(alias="flowType")
    inlet_size: str = Field(alias="inletSize")
    manufacturer: str
    model: str
    model_type: RegisterModelType = Field(alias="modelType")
    quantity: int
    register_cfm: float = Field(alias="registerCFM")
    register_fpm: float = Field(alias="registerFPM")
    register_nc: float = Field(alias="registerNC")
    register_size: str = Field(alias="registerSize")
    space_name: str = Field(alias="spaceName")
    space_number: str = Field(alias="spaceNumber")
    total_cfm: float = Field(alias="totalCFM")

    model_config = {"populate_by_name": True}


class APIProjectOutputRegisterSchedule(BaseModel):
    """API response for register schedule output."""

    errors: list[ErrorInfo]
    register_schedule: list[SpaceRegisterScheduleRow] = Field(alias="registerSchedule")

    model_config = {"populate_by_name": True}


# Calculated graph schemas
class MetaGraphDuctAdjacency(BaseModel):
    """Duct adjacency with flow rate."""

    id: str
    adjacency_type: Literal["DUCT"] = Field(alias="adjacencyType")
    duct_size: DuctSize | None = Field(default=None, alias="ductSize")
    duct_type_id: str | None = Field(default=None, alias="ductTypeId")
    flow_rate: float | None = Field(default=None, alias="flowRate")

    model_config = {"populate_by_name": True}


class MetaGraphLinkAdjacency(BaseModel):
    """Link adjacency."""

    id: str
    adjacency_type: Literal["LINK"] = Field(alias="adjacencyType")

    model_config = {"populate_by_name": True}


MetaGraphAdjacencyData = MetaGraphDuctAdjacency | MetaGraphLinkAdjacency


class MetaGraphNode(NodeData):
    """A graph node annotated with its calculated pressure."""

    id: str
    adjacencies: list[MetaGraphAdjacencyData]
    pressure: float | None = None


MetaGraph = dict[str, MetaGraphNode]


# Unified calculation response schemas (v0.4+)
class Airflows(BaseModel):
    """Supply, return, outside, relief, and exhaust airflow totals."""

    exhaust: float
    outside: float
    relief: float
    return_air: float = Field(alias="return")
    supply: float

    model_config = {"populate_by_name": True}


class ModeAirflows(BaseModel):
    """Design and required airflows for one equipment mode."""

    airflow_differential: dict[str, float] = Field(alias="airflowDifferential")
    design: Airflows
    required: Airflows
    space_peaks_sum: Airflows = Field(alias="spacePeaksSum")
    supply_sources: dict[str, float] = Field(alias="supplySources")
    month_hour: dict[str, float] | None = Field(default=None, alias="monthHour")

    model_config = {"populate_by_name": True}


class MaximumModeAirflows(BaseModel):
    """The peak design and required airflows across the project's modes."""

    airflow_differential: dict[str, float] = Field(alias="airflowDifferential")
    design: Airflows
    required: Airflows

    model_config = {"populate_by_name": True}


class ProjectScopeAirflows(BaseModel):
    """Mode-keyed airflows for a project, space, zone, or system."""

    by_mode: dict[str, ModeAirflows] = Field(alias="byMode")
    calculated_outside_airflow: dict[str, float] = Field(alias="calculatedOutsideAirflow")
    max: MaximumModeAirflows
    required_outside_airflow_components: dict[str, Any] = Field(
        alias="requiredOutsideAirflowComponents"
    )

    model_config = {"populate_by_name": True}


class CalcLoadsSection(BaseModel):
    """Cooling and heating loads for each project scope."""

    space_cooling_loads: dict[str, CoolingLoads] = Field(alias="spaceCoolingLoads")
    space_heating_loads: dict[str, HeatingLoads] = Field(alias="spaceHeatingLoads")
    system_cooling_loads: dict[str, CoolingLoads] = Field(alias="systemCoolingLoads")
    system_heating_loads: dict[str, HeatingLoads] = Field(alias="systemHeatingLoads")
    zone_cooling_loads: dict[str, CoolingLoads] = Field(alias="zoneCoolingLoads")
    zone_heating_loads: dict[str, HeatingLoads] = Field(alias="zoneHeatingLoads")

    model_config = {"populate_by_name": True}


class CalcVentilationSection(BaseModel):
    """Ventilation results keyed by project scope and equipment id."""

    project: dict[str, Any] | None = None
    spaces: dict[str, dict[str, Any]]
    systems: dict[str, dict[str, Any]]
    zones: dict[str, dict[str, Any]]
    equipment: dict[str, dict[str, Any]]


class CalcChecksumsSection(BaseModel):
    """Mode-keyed design checksums for each scope and equipment item."""

    project: dict[str, dict[str, float | None]] | None = None
    spaces: dict[str, dict[str, dict[str, float | None]]]
    systems: dict[str, dict[str, dict[str, float | None]]]
    zones: dict[str, dict[str, dict[str, float | None]]]
    equipment: dict[str, dict[str, dict[str, float | None]]]


class CalcAirflowsSection(BaseModel):
    """Mode-keyed airflow results for every project scope."""

    project: ProjectScopeAirflows | None = None
    spaces: dict[str, ProjectScopeAirflows]
    systems: dict[str, ProjectScopeAirflows]
    zones: dict[str, ProjectScopeAirflows]


class EquipmentSectionOutput(BaseModel):
    """Calculated outputs for one central or terminal unit.

    ``airflows`` and ``modes`` keep the component pipeline data verbatim:
    pipeline components are extensible and are keyed by project-defined mode
    and component ids.
    """

    scope: EquipmentProjectScope
    airflows: dict[str, Any] | None = None
    modes: dict[str, dict[str, Any]] | None = None


class APIProjectCalculations(BaseModel):
    """Response from ``GET /projects/{id}/calculations``.

    ``equipment`` is keyed by unit graph node ID. Each entry's ``scope`` names
    the system or zone the unit serves.
    """

    errors: list[ErrorInfo]
    flags: dict[str, list[dict[str, Any]]]
    loads: CalcLoadsSection | None = None
    register_schedule: list[SpaceRegisterScheduleRow] | None = Field(
        default=None, alias="registerSchedule"
    )
    graph: MetaGraph | None = None
    ventilation: CalcVentilationSection | None = None
    equipment: dict[str, EquipmentSectionOutput] | None = None
    checksums: CalcChecksumsSection | None = None
    airflows: CalcAirflowsSection | None = None

    model_config = {"populate_by_name": True}
