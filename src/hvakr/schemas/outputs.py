"""Output schema definitions for API responses."""

from enum import Enum
from typing import Any, Literal, Union

from pydantic import BaseModel, Field

from hvakr.schemas.common import Point
from hvakr.schemas.graph import (
    AdjacencyType,
    DuctAdjacencyData,
    FlowType,
    LinkAdjacencyData,
    NodeType,
    RegisterPlacementType,
    Selection,
    Size,
)


class APIOutputType(str, Enum):
    """Type of project output."""

    DRYSIDE_GRAPH = "dryside_graph"
    REGISTER_SCHEDULE = "register_schedule"
    LOADS = "loads"


class RegisterModelType(str, Enum):
    """Register model type."""

    CEILING_SQUARE = "ceilingSquare"
    CEILING_LINEAR = "ceilingLinear"


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


# Dry side graph schemas
class MetaDrySideNodeData(BaseModel):
    """Node data with pressure information."""

    # Coordinate data
    level: int
    point: Point
    # Pressure
    pressure: float | None = None
    # Node type and specific data
    node_type: NodeType = Field(alias="nodeType")
    # Register fields
    flow_rate: float | None = Field(default=None, alias="flowRate")
    flow_type: FlowType | None = Field(default=None, alias="flowType")
    placement_type: RegisterPlacementType | None = Field(default=None, alias="placementType")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    size: Size | None = None
    tag: str | None = None
    throw: float | None = None
    rotation: float | None = None
    space_ids: list[str] | None = Field(default=None, alias="spaceIds")
    # Fitting fields
    custom_loss_coefficients: dict[str, float] | None = Field(
        default=None, alias="customLossCoefficients"
    )
    custom_pressure_losses: dict[str, float] | None = Field(
        default=None, alias="customPressureLosses"
    )
    # Terminal/Central unit fields
    selections: dict[str, Selection] | None = None
    zone_id: str | None = Field(default=None, alias="zoneId")
    system_id: str | None = Field(default=None, alias="systemId")

    model_config = {"populate_by_name": True}


class MetaDrySideDuctAdjacency(BaseModel):
    """Duct adjacency with flow rate."""

    id: str
    adjacency_type: Literal["DUCT"] = Field(alias="adjacencyType")
    duct_size: dict[str, Any] | None = Field(default=None, alias="ductSize")
    duct_type_id: str | None = Field(default=None, alias="ductTypeId")
    flow_rate: float | None = Field(default=None, alias="flowRate")

    model_config = {"populate_by_name": True}


class MetaDrySideLinkAdjacency(BaseModel):
    """Link adjacency."""

    id: str
    adjacency_type: Literal["LINK"] = Field(alias="adjacencyType")

    model_config = {"populate_by_name": True}


MetaDrySideAdjacencyData = Union[MetaDrySideDuctAdjacency, MetaDrySideLinkAdjacency]


class MetaDrySideGraphNode(BaseModel):
    """A node in the dry side graph with metadata."""

    adjacencies: list[MetaDrySideDuctAdjacency | MetaDrySideLinkAdjacency]
    id: str
    # Node data
    level: int
    point: Point
    pressure: float | None = None
    node_type: NodeType = Field(alias="nodeType")
    # Additional node-specific fields
    flow_rate: float | None = Field(default=None, alias="flowRate")
    flow_type: FlowType | None = Field(default=None, alias="flowType")
    placement_type: RegisterPlacementType | None = Field(default=None, alias="placementType")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    size: Size | None = None
    tag: str | None = None
    throw: float | None = None
    rotation: float | None = None
    space_ids: list[str] | None = Field(default=None, alias="spaceIds")
    custom_loss_coefficients: dict[str, float] | None = Field(
        default=None, alias="customLossCoefficients"
    )
    custom_pressure_losses: dict[str, float] | None = Field(
        default=None, alias="customPressureLosses"
    )
    selections: dict[str, Selection] | None = None
    zone_id: str | None = Field(default=None, alias="zoneId")
    system_id: str | None = Field(default=None, alias="systemId")

    model_config = {"populate_by_name": True}


MetaDrySideGraph = dict[str, MetaDrySideGraphNode]


class APIProjectOutputDrySideGraph(BaseModel):
    """API response for dry side graph output."""

    dryside_graph: MetaDrySideGraph = Field(alias="drySideGraph")
    errors: list[ErrorInfo]

    model_config = {"populate_by_name": True}
