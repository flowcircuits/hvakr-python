"""Graph schema definitions for HVAC system topology."""

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from hvakr.schemas.common import Point, Size
from hvakr.schemas.equipment import EquipmentConfig


class FlowType(str, Enum):
    """Type of airflow in the HVAC system."""

    SUPPLY = "SUPPLY"
    RETURN = "RETURN"
    EXHAUST = "EXHAUST"


class NodeType(str, Enum):
    """Type of node in the HVAC graph."""

    REGISTER = "REGISTER"
    TERMINAL_UNIT = "TERMINAL_UNIT"
    CENTRAL_UNIT = "CENTRAL_UNIT"
    PORTAL = "PORTAL"
    FITTING = "FITTING"


class DuctSizeType(str, Enum):
    """Shape type for duct sizing."""

    CIRCLE = "CIRCLE"
    RECTANGLE = "RECTANGLE"


class RegisterPlacementType(str, Enum):
    """Placement type for registers."""

    CEILING = "CEILING"
    SIDEWALL = "SIDEWALL"


class AdjacencyType(str, Enum):
    """Type of connection between nodes."""

    DUCT = "DUCT"
    LINK = "LINK"


class CircleDuctSize(BaseModel):
    """Circular duct size specification."""

    duct_size_type: Literal["CIRCLE"] = Field(alias="ductSizeType")
    height: float

    model_config = {"populate_by_name": True}


class RectangleDuctSize(BaseModel):
    """Rectangular duct size specification."""

    duct_size_type: Literal["RECTANGLE"] = Field(alias="ductSizeType")
    height: float
    width: float

    model_config = {"populate_by_name": True}


DuctSize = Annotated[
    CircleDuctSize | RectangleDuctSize,
    Field(discriminator="duct_size_type"),
]


class RegisterSpecificData(BaseModel):
    """Register-specific data."""

    flow_rate: float | None = Field(default=None, alias="flowRate")
    flow_type: FlowType = Field(alias="flowType")
    placement_type: RegisterPlacementType = Field(alias="placementType")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    size: Size
    tag: str | None = None
    throw: float | None = None

    model_config = {"populate_by_name": True}


class RegisterNodeData(BaseModel):
    """Data for register nodes."""

    node_type: Literal["REGISTER"] = Field(alias="nodeType")
    flow_rate: float | None = Field(default=None, alias="flowRate")
    flow_type: FlowType = Field(alias="flowType")
    placement_type: RegisterPlacementType = Field(alias="placementType")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    size: Size
    tag: str | None = None
    throw: float | None = None
    rotation: float | None = None
    space_ids: list[str] | None = Field(default=None, alias="spaceIds")

    model_config = {"populate_by_name": True}


class FittingNodeData(BaseModel):
    """Data for fitting nodes."""

    node_type: Literal["FITTING"] = Field(alias="nodeType")
    custom_loss_coefficients: dict[str, float] | None = Field(
        default=None, alias="customLossCoefficients"
    )
    custom_pressure_losses: dict[str, float] | None = Field(
        default=None, alias="customPressureLosses"
    )

    model_config = {"populate_by_name": True}


class Selection(BaseModel):
    """Equipment selection data."""

    leaving_air_temp: float | None = Field(default=None, alias="leavingAirTemp")
    product_id: str = Field(alias="productId")
    quantity: int

    model_config = {"populate_by_name": True}


class TerminalUnitNodeData(EquipmentConfig):
    """Data for terminal unit nodes, including their equipment configuration."""

    node_type: Literal["TERMINAL_UNIT"] = Field(alias="nodeType")
    rotation: float | None = None
    width: float | None = None
    height: float | None = None
    product_id: str | None = Field(default=None, alias="productId")
    cost: float | None = Field(default=None, ge=0)
    selections: dict[str, Selection] | None = None
    zone_id: str = Field(alias="zoneId")


class CentralUnitNodeData(EquipmentConfig):
    """Data for central unit nodes, including their equipment configuration."""

    node_type: Literal["CENTRAL_UNIT"] = Field(alias="nodeType")
    rotation: float | None = None
    width: float | None = None
    height: float | None = None
    product_id: str | None = Field(default=None, alias="productId")
    cost: float | None = Field(default=None, ge=0)
    selections: dict[str, Selection] | None = None
    system_id: str = Field(alias="systemId")


class PortalNodeData(BaseModel):
    """Data for portal nodes."""

    node_type: Literal["PORTAL"] = Field(alias="nodeType")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    flow_type: FlowType = Field(alias="flowType")

    model_config = {"populate_by_name": True}


AssociatedNodeData = Annotated[
    RegisterNodeData
    | TerminalUnitNodeData
    | CentralUnitNodeData
    | FittingNodeData
    | PortalNodeData,
    Field(discriminator="node_type"),
]


class CoordinateNodeData(BaseModel):
    """Coordinate data for nodes."""

    level: int
    point: Point


class DuctAdjacencyData(BaseModel):
    """Data for duct adjacencies."""

    adjacency_type: Literal["DUCT"] = Field(alias="adjacencyType")
    duct_size: CircleDuctSize | RectangleDuctSize | None = Field(default=None, alias="ductSize")
    duct_type_id: str | None = Field(default=None, alias="ductTypeId")

    model_config = {"populate_by_name": True}


class LinkAdjacencyData(BaseModel):
    """Data for link adjacencies."""

    adjacency_type: Literal["LINK"] = Field(alias="adjacencyType")

    model_config = {"populate_by_name": True}


AssociatedAdjacencyData = Annotated[
    DuctAdjacencyData | LinkAdjacencyData,
    Field(discriminator="adjacency_type"),
]


class GraphAdjacency(BaseModel):
    """Graph adjacency with ID and data."""

    id: str
    adjacency_type: AdjacencyType = Field(alias="adjacencyType")
    # Duct-specific fields
    duct_size: CircleDuctSize | RectangleDuctSize | None = Field(default=None, alias="ductSize")
    duct_type_id: str | None = Field(default=None, alias="ductTypeId")

    model_config = {"populate_by_name": True}


class NodeData(EquipmentConfig):
    """Fields of every node type in one model; ``node_type`` says which apply.

    The equipment configuration fields apply to central and terminal unit
    nodes. A unit node can be unplaced: it omits both ``level`` and ``point``.
    Every other node type has both.
    """

    level: int | None = None
    point: Point | None = None
    node_type: NodeType = Field(alias="nodeType")
    # Register fields
    flow_rate: float | None = Field(default=None, alias="flowRate")
    flow_type: FlowType | None = Field(default=None, alias="flowType")
    placement_type: RegisterPlacementType | None = Field(default=None, alias="placementType")
    size: Size | None = None
    tag: str | None = None
    throw: float | None = None
    space_ids: list[str] | None = Field(default=None, alias="spaceIds")
    # Register and unit fields
    rotation: float | None = None
    width: float | None = None
    height: float | None = None
    product_id: str | None = Field(default=None, alias="productId")
    # Fitting fields
    custom_loss_coefficients: dict[str, float] | None = Field(
        default=None, alias="customLossCoefficients"
    )
    custom_pressure_losses: dict[str, float] | None = Field(
        default=None, alias="customPressureLosses"
    )
    # Terminal/Central unit fields
    cost: float | None = Field(default=None, ge=0)
    selections: dict[str, Selection] | None = None
    zone_id: str | None = Field(default=None, alias="zoneId")
    system_id: str | None = Field(default=None, alias="systemId")

    @model_validator(mode="after")
    def check_placement(self) -> "NodeData":
        """Only unit nodes can be unplaced, and only with both coordinates omitted."""
        if (self.level is None) != (self.point is None):
            raise ValueError("level and point must both be set or both be omitted")
        if self.level is None and self.node_type not in (
            NodeType.CENTRAL_UNIT,
            NodeType.TERMINAL_UNIT,
        ):
            raise ValueError(f"{self.node_type.value} nodes need level and point")
        return self


class GraphNode(NodeData):
    """A node in the HVAC graph."""

    id: str
    adjacencies: list[GraphAdjacency]


Graph = dict[str, GraphNode]
