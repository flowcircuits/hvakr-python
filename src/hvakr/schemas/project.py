"""Project schema definitions."""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from hvakr.schemas.common import Box, DisplayUnitSystemId, Point, Rect, Size
from hvakr.schemas.graph import DuctSize, FlowType, Graph, RegisterPlacementType


# Weather spec enums
class CoolingPercent(str, Enum):
    """Cooling design percentage."""

    P0_4 = "0.4"
    P2 = "2"
    P5 = "5"
    P10 = "10"


class HeatingPercent(str, Enum):
    """Heating design percentage."""

    P99 = "99"
    P99_6 = "99.6"


class MapType(str, Enum):
    """Map display type."""

    ROADMAP = "roadmap"
    SATELLITE = "satellite"
    HYBRID = "hybrid"


class ProjectType(str, Enum):
    """Type of project."""

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"


class VentilationStandard(str, Enum):
    """Ventilation standard."""

    ASHRAE_2022 = "ASHRAE 62.1 / 170 (2022)"
    ASHRAE_2025 = "ASHRAE 62.1 / 170 (2025)"


class ProjectUserRole(int, Enum):
    """User role in a project."""

    NONE = 0
    VIEWER = 1
    MEMBER = 4
    ADMIN = 8
    OWNER = 10


class InfiltrationRequirementMethod(str, Enum):
    """Method for calculating infiltration requirements."""

    AREA = "AREA"
    FLOW_RATE = "FLOW_RATE"
    PERIMETER = "PERIMETER"
    VOLUME = "VOLUME"


class EdgeExposure(str, Enum):
    """Cardinal direction for edge exposure."""

    N = "N"
    E = "E"
    S = "S"
    W = "W"


class OutsideAirMethod(str, Enum):
    """Method for calculating outside air."""

    SUM_OF_SPACES = "SUM_OF_SPACES"
    PERCENT = "PERCENT"
    CUSTOM = "CUSTOM"
    MULTI_ZONE = "MULTI_ZONE"


class LoadCondition(str, Enum):
    """The design condition represented by an equipment mode."""

    COOLING = "COOLING"
    HEATING = "HEATING"


class EquipmentComponentType(str, Enum):
    """Component types supported by a modular equipment configuration."""

    OUTSIDE_AIR_INTAKE = "OUTSIDE_AIR_INTAKE"
    ENERGY_RECOVERY_UNIT = "ENERGY_RECOVERY_UNIT"
    RETURN_AIR_INTAKE = "RETURN_AIR_INTAKE"
    COOLING_COIL = "COOLING_COIL"
    HEATING_COIL = "HEATING_COIL"
    EQUIPMENT_INEFFICIENCY = "EQUIPMENT_INEFFICIENCY"
    HUMIDIFIER = "HUMIDIFIER"
    DEHUMIDIFIER = "DEHUMIDIFIER"
    EQUIPMENT_INLET = "EQUIPMENT_INLET"
    EQUIPMENT_OUTLET = "EQUIPMENT_OUTLET"


class EquipmentInletMethod(str, Enum):
    """Methods for configuring a terminal unit's upstream inlet airflow."""

    SUM_OF_SPACES_OA = "SUM_OF_SPACES_OA"
    PERCENT_SUPPLY = "PERCENT_SUPPLY"
    CUSTOM = "CUSTOM"


class CoolingCoilType(int, Enum):
    """Type of cooling coil."""

    WATER = 0
    EXPANSION = 1


class HeatingCoilType(int, Enum):
    """Type of heating coil."""

    WATER = 0
    EXPANSION = 1
    GAS = 2
    ELECTRIC = 3


class FittingType(str, Enum):
    """Type of duct fitting."""

    ELBOW = "ELBOW"
    WYE = "WYE"
    TRANSITION = "TRANSITION"


class TransitionType(str, Enum):
    """Type of duct transition."""

    EXPANSION = "EXPANSION"
    REDUCTION = "REDUCTION"


class WyeType(str, Enum):
    """Type of wye fitting."""

    DIVERGENT = "DIVERGENT"
    CONVERGENT = "CONVERGENT"


class TerminalUnitInletSize(str, Enum):
    """Terminal unit inlet size."""

    SIZE_6 = "6"
    SIZE_8 = "8"
    SIZE_10 = "10"
    SIZE_12 = "12"
    SIZE_14 = "14"
    SIZE_16 = "16"
    SIZE_24X16 = "24x16"


class TerminalUnitOutsideAirMethod(int, Enum):
    """Method for terminal unit outside air calculation."""

    SUM_OF_SPACES = 0
    PERCENT = 1
    CUSTOM = 2


class PipeMaterialType(str, Enum):
    """Pipe material type."""

    STEEL = "STEEL"
    COPPER = "COPPER"


class DefaultRegisterType(str, Enum):
    """Default register sizing category."""

    LARGE = "LARGE"
    NORMAL = "NORMAL"
    SMALL = "SMALL"


class ReportFileType(str, Enum):
    """Report output file type."""

    PDF = "PDF"
    CSV = "CSV"
    DOCX = "DOCX"
    ZIP = "ZIP"


class LengthUnit(str, Enum):
    """Length unit for sheet scales."""

    IN = "IN"
    FT = "FT"
    MM = "MM"
    M = "M"


class SheetType(str, Enum):
    """Sheet drawing type."""

    ENLARGED_FLOOR_PLAN = "Enlarged Floor Plan"
    OVERALL_FLOOR_PLAN = "Overall Floor Plan"
    REFLECTED_CEILING_PLAN = "Reflected Ceiling Plan"
    FURNITURE_PLAN = "Furniture Plan"
    EXTERIOR_ELEVATION = "Exterior Elevation"
    INTERIOR_ELEVATION = "Interior Elevation"


# Weather and map specs
class WeatherSpec(BaseModel):
    """Weather specification for a project."""

    cool_db: float | None = Field(default=None, alias="coolDb")
    cool_percent: CoolingPercent | None = Field(default=None, alias="coolPercent")
    cool_wb: float | None = Field(default=None, alias="coolWb")
    heat_db: float | None = Field(default=None, alias="heatDb")
    heat_percent: HeatingPercent | None = Field(default=None, alias="heatPercent")
    loading: bool | None = None
    nearest_weather_station_ids: list[str] | None = Field(
        default=None, alias="nearestWeatherStationIds"
    )
    selected_station_id: str | None = Field(default=None, alias="selectedStationId")

    model_config = {"populate_by_name": True}


class MapSpec(BaseModel):
    """Map display specification."""

    active: bool | None = None
    crop_box: Rect | None = Field(default=None, alias="cropBox")
    locked: bool | None = None
    type: MapType | None = None
    x: float | None = None
    x_offset: float | None = Field(default=None, alias="xOffset")
    y: float | None = None
    y_offset: float | None = Field(default=None, alias="yOffset")
    zoom: float | None = None

    model_config = {"populate_by_name": True}


# Project metadata
class Constraint(BaseModel):
    """Project constraint."""

    description: str | None = None
    name: str | None = None
    timestamp: float


class Contact(BaseModel):
    """Project contact."""

    address: str | None = None
    company: str | None = None
    email: str | None = None
    name: str | None = None
    phone: str | None = None
    role: str | None = None
    timestamp: float
    trade: str | None = None


class Standard(BaseModel):
    """Project standard."""

    description: str | None = None
    name: str | None = None
    timestamp: float


class BuildingData(BaseModel):
    """Building information."""

    area: float | None = None
    ashrae_building_type_id: str | None = Field(default=None, alias="ashraeBuildingTypeId")
    description: str | None = None
    name: str | None = None
    occupancy: float | None = None
    plan_rotation: float | None = Field(default=None, alias="planRotation")
    stories: int | None = None

    model_config = {"populate_by_name": True}


class Revision(BaseModel):
    """Project revision."""

    description: str | None = None
    id: str
    log: str | None = None
    saved_by: str = Field(alias="savedBy")
    timestamp: float

    model_config = {"populate_by_name": True}


class ProjectUserData(BaseModel):
    """User data within a project."""

    active: bool | None = None
    first_name: str | None = Field(default=None, alias="firstName")
    last_active: float | None = Field(default=None, alias="lastActive")
    last_name: str | None = Field(default=None, alias="lastName")
    pending_sign_up: bool | None = Field(default=None, alias="pendingSignUp")
    profile_picture: str | None = Field(default=None, alias="profilePicture")
    role: ProjectUserRole

    model_config = {"populate_by_name": True}


class EquipmentMode(BaseModel):
    """A project-wide operating mode used by all equipment configurations."""

    id: str
    load_condition: LoadCondition = Field(alias="loadCondition")
    name: str
    description: str

    model_config = {"populate_by_name": True}


class UpstreamEquipmentLinkEndpoint(BaseModel):
    """The outlet selected on an upstream equipment item."""

    id: str
    outlet_id: str = Field(alias="outletId")

    model_config = {"populate_by_name": True}


class EquipmentLinkData(BaseModel):
    """Connects one equipment outlet to another equipment inlet."""

    upstream_equipment: UpstreamEquipmentLinkEndpoint = Field(alias="upstreamEquipment")
    downstream_equipment: "DownstreamEquipmentLinkEndpoint" = Field(alias="downstreamEquipment")

    model_config = {"populate_by_name": True}


class DownstreamEquipmentLinkEndpoint(BaseModel):
    """The inlet selected on a downstream equipment item."""

    id: str
    inlet_id: str = Field(alias="inletId")

    model_config = {"populate_by_name": True}


class EquipmentLink(EquipmentLinkData):
    """A persisted equipment link."""

    id: str


DEFAULT_COOLING_MODE_ID = "cooling_mode"
DEFAULT_HEATING_MODE_ID = "heating_mode"
DEFAULT_EQUIPMENT_MODES: dict[str, EquipmentMode] = {
    DEFAULT_COOLING_MODE_ID: EquipmentMode(
        id=DEFAULT_COOLING_MODE_ID,
        loadCondition=LoadCondition.COOLING,
        name="Cooling",
        description="",
    ),
    DEFAULT_HEATING_MODE_ID: EquipmentMode(
        id=DEFAULT_HEATING_MODE_ID,
        loadCondition=LoadCondition.HEATING,
        name="Heating",
        description="",
    ),
}


# Fittings configuration
class ElbowData(BaseModel):
    """Elbow fitting data."""

    fitting_type: Literal["ELBOW"] = Field(alias="fittingType")
    loss_coefficient: float | None = Field(default=None, alias="lossCoefficient")

    model_config = {"populate_by_name": True}


class TransitionData(BaseModel):
    """Transition fitting data."""

    fitting_type: Literal["TRANSITION"] = Field(alias="fittingType")
    loss_coefficient: float | None = Field(default=None, alias="lossCoefficient")
    transition_type: TransitionType = Field(alias="transitionType")

    model_config = {"populate_by_name": True}


class WyeData(BaseModel):
    """Wye fitting data."""

    branch_loss_coefficient: float | None = Field(default=None, alias="branchLossCoefficient")
    fitting_type: Literal["WYE"] = Field(alias="fittingType")
    main_loss_coefficient: float | None = Field(default=None, alias="mainLossCoefficient")
    wye_type: WyeType = Field(alias="wyeType")

    model_config = {"populate_by_name": True}


class FittingsConfig(BaseModel):
    """Fittings configuration."""

    convergent_wye: dict[str, float] | None = Field(default=None, alias="CONVERGENT_WYE")
    divergent_wye: dict[str, float] | None = Field(default=None, alias="DIVERGENT_WYE")
    elbow: dict[str, float] | None = Field(default=None, alias="ELBOW")
    expansion_transition: dict[str, float] | None = Field(
        default=None, alias="EXPANSION_TRANSITION"
    )
    reduction_transition: dict[str, float] | None = Field(
        default=None, alias="REDUCTION_TRANSITION"
    )

    model_config = {"populate_by_name": True}


class DuctSizingData(BaseModel):
    """Duct sizing data."""

    duct_sizes: dict[str, DuctSize] | None = Field(default=None, alias="ductSizes")
    duct_sizing_hash: str | None = Field(default=None, alias="ductSizingHash")

    model_config = {"populate_by_name": True}


class DrySideData(BaseModel):
    """Dry side configuration."""

    fittings: FittingsConfig | None = None
    flow_colors: dict[str, str] | None = Field(default=None, alias="flowColors")
    sizing_data: DuctSizingData | None = Field(default=None, alias="sizingData")

    model_config = {"populate_by_name": True}


class ComputedProjectData(BaseModel):
    """Computed project data."""

    owner: str | None = Field(default=None, alias="_owner")
    user_emails: list[str] | None = Field(default=None, alias="_userEmails")

    model_config = {"populate_by_name": True}


# Space components
class SkylightData(BaseModel):
    """Skylight data."""

    height: float
    rotation: float | None = None
    width: float
    window_type_id: str | None = Field(default=None, alias="windowTypeId")
    x: float
    y: float

    model_config = {"populate_by_name": True}


class InternalShadingData(BaseModel):
    """Internal shading data."""

    beam_iac0: float | None = Field(default=None, alias="beamIAC0")
    beam_iac60: float | None = Field(default=None, alias="beamIAC60")
    diffuse_iac: float | None = Field(default=None, alias="diffuseIAC")
    radiant_fraction: float | None = Field(default=None, alias="radiantFraction")

    model_config = {"populate_by_name": True}


class ExternalShadingData(BaseModel):
    """External shading data."""

    side_overhang_depth: float | None = Field(default=None, alias="sideOverhangDepth")
    side_overhang_offset: float | None = Field(default=None, alias="sideOverhangOffset")
    top_overhang_depth: float | None = Field(default=None, alias="topOverhangDepth")
    top_overhang_offset: float | None = Field(default=None, alias="topOverhangOffset")

    model_config = {"populate_by_name": True}


class WindowData(BaseModel):
    """Window data."""

    bottom: float | None = None
    external_shading: bool | None = Field(default=None, alias="externalShading")
    external_shading_data: ExternalShadingData | None = Field(
        default=None, alias="externalShadingData"
    )
    height: float
    internal_shading: bool | None = Field(default=None, alias="internalShading")
    internal_shading_data: InternalShadingData | None = Field(
        default=None, alias="internalShadingData"
    )
    width: float
    window_type_id: str | None = Field(default=None, alias="windowTypeId")
    x: float
    y: float

    model_config = {"populate_by_name": True}


class DoorData(BaseModel):
    """Door data."""

    door_type_id: str | None = Field(default=None, alias="doorTypeId")
    height: float
    width: float
    x: float
    y: float

    model_config = {"populate_by_name": True}


class Edge(BaseModel):
    """Edge (wall segment) data."""

    apply_load_to_ceiling: bool | None = Field(default=None, alias="applyLoadToCeiling")
    doors: dict[str, DoorData] | None = None
    index: int
    name: str | None = None
    surface_tilt: float | None = Field(default=None, alias="surfaceTilt")
    wall_type_id: str | None = Field(default=None, alias="wallTypeId")
    windows: dict[str, WindowData] | None = None
    x1: float
    x2: float
    y1: float
    y2: float

    model_config = {"populate_by_name": True}


class SpaceData(BaseModel):
    """Space data."""

    design_airflows_by_mode: dict[str, "SpaceDesignAirflows"] | None = Field(
        default=None, alias="designAirflowsByMode"
    )
    airflow_requirements_by_load_condition: (
        dict[LoadCondition, "SpaceAirflowRequirements"] | None
    ) = Field(default=None, alias="airflowRequirementsByLoadCondition")
    apply_roof_load_to_ceiling: bool | None = Field(default=None, alias="applyRoofLoadToCeiling")
    ceiling_height: float | None = Field(default=None, alias="ceilingHeight")
    creation_source: Literal[
        "API", "API_REVIT", "AUTO", "LEGACY", "MERGE", "PASTE", "POLYGON", "RECTANGLE", "SPLIT"
    ] = Field(alias="creationSource")
    edges: dict[str, Edge]
    exhaust_units: float | None = Field(default=None, alias="exhaustUnits")
    infiltration_use_separate_winter_reqs: bool | None = Field(
        default=None, alias="infiltrationUseSeparateWinterReqs"
    )
    level: int
    misc_heating_load: float | None = Field(default=None, alias="miscHeatingLoad")
    misc_latent_cooling_load: float | None = Field(default=None, alias="miscLatentCoolingLoad")
    misc_sensible_cooling_load: float | None = Field(default=None, alias="miscSensibleCoolingLoad")
    name: str | None = None
    number: str | None = None
    occupancy: float | None = None
    processed: bool | None = None
    revit_id: str | None = Field(default=None, alias="revitId")
    roof_azimuth: float | None = Field(default=None, alias="roofAzimuth")
    roof_pitch: float | None = Field(default=None, alias="roofPitch")
    roof_type_id: str | None = Field(default=None, alias="roofTypeId")
    skylights: dict[str, SkylightData] | None = None
    slab_height: float | None = Field(default=None, alias="slabHeight")
    slab_type_id: str | None = Field(default=None, alias="slabTypeId")
    space_type_id: str | None = Field(default=None, alias="spaceTypeId")
    space_name_and_number_input_hash: str | None = Field(
        default=None, alias="spaceNameAndNumberInputHash"
    )
    suggested: bool | None = None
    suggested_space_name: str | None = Field(default=None, alias="suggestedSpaceName")
    suggested_space_number: str | None = Field(default=None, alias="suggestedSpaceNumber")
    zone_id: str | None = Field(default=None, alias="zoneId")

    model_config = {"populate_by_name": True}


# Modular equipment configuration
class SpaceDesignAirflows(BaseModel):
    """Per-mode design airflow overrides for a space."""

    air_transfer_in: float | None = Field(default=None, alias="airTransferIn")
    air_transfer_out: float | None = Field(default=None, alias="airTransferOut")
    exhaust_air: float | None = Field(default=None, alias="exhaustAir")
    outside_air: float | None = Field(default=None, alias="outsideAir")
    return_air: float | None = Field(default=None, alias="returnAir")
    supply_air: float | None = Field(default=None, alias="supplyAir")

    model_config = {"populate_by_name": True}


class SpaceAirflowRequirements(BaseModel):
    """Per-load-condition ventilation and infiltration overrides for a space."""

    infiltration_ach_req: float | None = Field(default=None, alias="infiltrationAchReq")
    infiltration_area_req: float | None = Field(default=None, alias="infiltrationAreaReq")
    infiltration_flow_rate_req: float | None = Field(default=None, alias="infiltrationFlowRateReq")
    infiltration_lf_req: float | None = Field(default=None, alias="infiltrationLfReq")
    infiltration_req_method: InfiltrationRequirementMethod | None = Field(
        default=None, alias="infiltrationReqMethod"
    )
    ventilation_req: float | None = Field(default=None, alias="ventilationReq")

    model_config = {"populate_by_name": True}


class EquipmentComponent(BaseModel):
    """A component in the ordered equipment pipeline."""

    id: str
    type: EquipmentComponentType


class EquipmentComponentConfiguration(BaseModel):
    """Configuration for one component in one operating mode.

    The component type determines which optional fields apply. Keeping the
    shared wire fields together mirrors the API's component registry while
    retaining an extensible model for newly introduced components.
    """

    component_type: EquipmentComponentType = Field(alias="componentType")
    method: OutsideAirMethod | EquipmentInletMethod | None = None
    percentage: float | None = None
    flow_rate: float | None = Field(default=None, alias="flowRate")
    duct_heat_gain: float | None = Field(default=None, alias="ductHeatGain")
    duct_leakage_percent: float | None = Field(default=None, alias="ductLeakagePercent")
    erv_wheel_effectiveness: float | None = Field(default=None, alias="ervWheelEffectiveness")
    relief_enabled: bool | None = Field(default=None, alias="reliefEnabled")
    target_temperature: float | None = Field(default=None, alias="targetTemperature")
    type: int | None = None
    water_delta_t: float | None = Field(default=None, alias="waterDeltaT")
    sensible_heat_gain: dict[str, Any] | None = Field(default=None, alias="sensibleHeatGain")
    decoupled: bool | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}

    @model_validator(mode="before")
    @classmethod
    def resolve_method_for_component_type(cls, data: Any) -> Any:
        """Use the component type to disambiguate overlapping method values."""
        if not isinstance(data, dict) or data.get("method") is None:
            return data

        component_type = data.get("componentType", data.get("component_type"))
        if component_type == EquipmentComponentType.EQUIPMENT_INLET:
            data = data.copy()
            data["method"] = EquipmentInletMethod(data["method"])
        return data


class ComponentConfiguration(BaseModel):
    """Enabled state and configuration of a component for a single mode."""

    enabled: bool
    configuration: EquipmentComponentConfiguration


class EquipmentInletData(BaseModel):
    """Terminal-unit inlet configuration shared by all modes."""

    enabled: bool
    configuration: EquipmentComponentConfiguration


class EquipmentData(BaseModel):
    """Shared modular equipment configuration for central and terminal units."""

    components: list[EquipmentComponent] | None = None
    component_configs_by_mode: dict[str, dict[str, ComponentConfiguration]] | None = Field(
        default=None, alias="componentConfigsByMode"
    )
    duct_heat_gain: float | None = Field(default=None, alias="ductHeatGain")
    duct_leakage_percent: float | None = Field(default=None, alias="ductLeakagePercent")
    misc_inefficiencies: float | None = Field(default=None, alias="miscInefficiencies")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    inlet_data: EquipmentInletData | None = Field(default=None, alias="inletData")

    model_config = {"populate_by_name": True}


class DiversityData(BaseModel):
    """Diversity data."""

    equipment: float | None = None
    lighting: float | None = None
    occupancy: float | None = None


class CentralUnitDimensionData(BaseModel):
    """Central unit dimension data."""

    length: float | None = None
    width: float | None = None


class EnergySchedule(BaseModel):
    """Operating schedule used for central-unit energy calculations."""

    occupied_hours: dict[str, Any] | None = Field(default=None, alias="occupiedHours")
    warmup_hours: float | None = Field(default=None, alias="warmupHours")
    warmup_multiplier: float | None = Field(default=None, alias="warmupMultiplier")

    model_config = {"populate_by_name": True}


class EquipmentEfficiency(BaseModel):
    """Central-unit heating and cooling efficiency inputs."""

    heating_type: Literal["heatPump", "gasFurnace"] | None = Field(
        default=None, alias="heatingType"
    )
    cooling_seer: float | None = Field(default=None, alias="coolingSeer")
    heating_cop: float | None = Field(default=None, alias="heatingCop")
    heating_afue: float | None = Field(default=None, alias="heatingAfue")

    model_config = {"populate_by_name": True}


class EnergyConfiguration(BaseModel):
    """Energy configuration attached to a central equipment configuration."""

    schedule: EnergySchedule | None = None
    efficiency: EquipmentEfficiency | None = None


class CentralUnitConfiguration(EquipmentData):
    """Modular central-unit equipment configuration."""

    dimension_data: CentralUnitDimensionData | None = Field(default=None, alias="dimensionData")
    energy_configuration: EnergyConfiguration | None = Field(
        default=None, alias="energyConfiguration"
    )


class SystemData(BaseModel):
    """System data."""

    equipment_config: CentralUnitConfiguration | None = Field(default=None, alias="equipmentConfig")
    color: str | None = None
    configured: bool | None = None
    diversity_data: DiversityData | None = Field(default=None, alias="diversityData")
    name: str | None = None

    model_config = {"populate_by_name": True}


# Terminal unit / Zone configuration
class TerminalUnitDimensionData(BaseModel):
    """Terminal unit dimension data."""

    inlet_size: TerminalUnitInletSize | None = Field(default=None, alias="inletSize")

    model_config = {"populate_by_name": True}


class TerminalUnitConfiguration(EquipmentData):
    """Modular terminal-unit equipment configuration."""

    dimension_data: TerminalUnitDimensionData | None = Field(default=None, alias="dimensionData")


class ZoneData(BaseModel):
    """Zone data."""

    color: str | None = None
    configured: bool | None = None
    equipment_config: TerminalUnitConfiguration | None = Field(
        default=None, alias="equipmentConfig"
    )
    name: str | None = None
    system_id: str | None = Field(default=None, alias="systemId")

    model_config = {"populate_by_name": True}


# Type data models
class BranchTypeData(BaseModel):
    """Branch type data."""

    loss_coefficient: float | None = Field(default=None, alias="lossCoefficient")
    name: str | None = None

    model_config = {"populate_by_name": True}


class DeadlineData(BaseModel):
    """Deadline data."""

    complete: bool
    date: float
    name: str | None = None
    timestamp: float | None = None


class DoorTypeData(BaseModel):
    """Door type data."""

    name: str | None = None
    open_fraction: float | None = Field(default=None, alias="openFraction")
    seals: bool | None = None
    surface_absorptance: float | None = Field(default=None, alias="surfaceAbsorptance")
    timestamp: float | None = None
    u_value: float | None = Field(default=None, alias="uValue")

    model_config = {"populate_by_name": True}


class DuctTypeData(BaseModel):
    """Duct type data."""

    color: str | None = None
    liner_thickness: float | None = Field(default=None, alias="linerThickness")
    max_height: float | None = Field(default=None, alias="maxHeight")
    max_pressure_drop_rate: float | None = Field(default=None, alias="maxPressureDropRate")
    max_velocity: float | None = Field(default=None, alias="maxVelocity")
    name: str | None = None
    timestamp: float | None = None

    model_config = {"populate_by_name": True}


class PipeTypeData(BaseModel):
    """Pipe type data."""

    insulation: float | None = None
    material: PipeMaterialType | None = None
    max_pressure_drop_rate: float | None = Field(default=None, alias="maxPressureDropRate")
    max_velocity: float | None = Field(default=None, alias="maxVelocity")
    name: str | None = None

    model_config = {"populate_by_name": True}


class RegisterSpecConstraints(BaseModel):
    """Constraints applied to a register specification."""

    max_cfm: float | None = Field(default=None, alias="maxCFM")
    max_fpm: float | None = Field(default=None, alias="maxFPM")
    max_nc: float | None = Field(default=None, alias="maxNC")
    register_model_id: str | None = Field(default=None, alias="registerModelId")

    model_config = {"populate_by_name": True}


class RegisterTypeData(BaseModel):
    """Register type data.

    Extends RegisterSpecificData with default-type metadata.
    """

    flow_rate: float | None = Field(default=None, alias="flowRate")
    flow_type: FlowType = Field(alias="flowType")
    placement_type: RegisterPlacementType = Field(alias="placementType")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    size: Size
    tag: str | None = None
    throw: float | None = None
    default_type: DefaultRegisterType | None = Field(default=None, alias="defaultType")
    name: str | None = None
    timestamp: float | None = None

    model_config = {"populate_by_name": True}


class ReportTemplateOption(BaseModel):
    """A configurable option on a report template."""

    id: str
    label: str
    type: Literal["checkbox", "select"]
    value: bool | str
    options: dict[str, str] | None = None


class ReportTemplate(BaseModel):
    """A report template definition."""

    file_type: ReportFileType = Field(alias="fileType")
    id: str
    name: str
    options: dict[str, ReportTemplateOption] | None = None

    model_config = {"populate_by_name": True}


class APIReport(BaseModel):
    """Public report projection returned by an expanded project."""

    id: str
    name: str
    status: Literal["pending", "completed", "failed"]
    download_url: str | None = Field(default=None, alias="downloadUrl")
    date: float
    output_file_type: ReportFileType | None = Field(default=None, alias="outputFileType")
    progress: float | None = None

    model_config = {"populate_by_name": True}


class ReportData(BaseModel):
    """Report data."""

    access_token: str = Field(alias="accessToken")
    date: float
    display_unit_system_id: DisplayUnitSystemId = Field(alias="displayUnitSystemId")
    file_name: str = Field(alias="fileName")
    name: str
    pending: bool
    template: ReportTemplate

    model_config = {"populate_by_name": True}


class RoofTypeData(BaseModel):
    """Roof type data."""

    ashrae_roof_type_id: str | None = Field(default=None, alias="ashraeRoofTypeId")
    color: str | None = None
    name: str | None = None
    surface_absorptance: float | None = Field(default=None, alias="surfaceAbsorptance")
    timestamp: float | None = None
    u_value: float | None = Field(default=None, alias="uValue")
    unconditioned_cooling_temp_f: float | None = Field(
        default=None, alias="unconditionedCoolingTempF"
    )
    unconditioned_heating_temp_f: float | None = Field(
        default=None, alias="unconditionedHeatingTempF"
    )

    model_config = {"populate_by_name": True}


class SheetFileData(BaseModel):
    """Sheet file data."""

    page_count: float | None = Field(default=None, alias="pageCount")
    processing_finish_time: float | None = Field(default=None, alias="processingFinishTime")
    processing_start_time: float | None = Field(default=None, alias="processingStartTime")
    sheet_number_box: list[Point] | None = Field(default=None, alias="sheetNumberBox")
    source_file_name: str = Field(alias="sourceFileName")
    timestamp: float
    upload_finish_time: float | None = Field(default=None, alias="uploadFinishTime")
    upload_start_time: float = Field(alias="uploadStartTime")
    url: str

    model_config = {"populate_by_name": True}


class SheetPlacementData(BaseModel):
    """Placement of a sheet within a project."""

    crop_box: Box | None = Field(default=None, alias="cropBox")
    is_locked: bool | None = Field(default=None, alias="isLocked")
    level: float
    rotation: float | None = None
    x: float
    y: float

    model_config = {"populate_by_name": True}


class SheetAnnotation(BaseModel):
    """Annotation on a sheet."""

    confidence: float | None = None
    polygon: list[Point]
    text: str
    type: str


class CustomScaleInfo(BaseModel):
    """Custom scale information for a sheet."""

    left_scale: float | None = Field(default=None, alias="leftScale")
    left_unit: LengthUnit | None = Field(default=None, alias="leftUnit")
    right_scale: float | None = Field(default=None, alias="rightScale")
    right_unit: LengthUnit | None = Field(default=None, alias="rightUnit")

    model_config = {"populate_by_name": True}


class SheetVersionData(BaseModel):
    """Version data for a sheet."""

    access_token: str = Field(alias="accessToken")
    image_file_name: str = Field(alias="imageFileName")
    page_number: float = Field(alias="pageNumber")
    sheet_file_id: str = Field(alias="sheetFileId")
    sheet_file_page_id: str = Field(alias="sheetFilePageId")
    source_file_name: str = Field(alias="sourceFileName")

    model_config = {"populate_by_name": True}


class SheetData(BaseModel):
    """Sheet data."""

    active_sheet_file_page_id: str | None = Field(default=None, alias="activeSheetFilePageId")
    placements: dict[str, SheetPlacementData] | None = None
    sheet_type: SheetType | None = Field(default=None, alias="sheetType")

    model_config = {"populate_by_name": True}


class SlabTypeData(BaseModel):
    """Slab type data."""

    color: str | None = None
    f_factor: float | None = Field(default=None, alias="fFactor")
    name: str | None = None
    timestamp: float | None = None
    u_value: float | None = Field(default=None, alias="uValue")
    unconditioned_cooling_temp_f: float | None = Field(
        default=None, alias="unconditionedCoolingTempF"
    )
    unconditioned_heating_temp_f: float | None = Field(
        default=None, alias="unconditionedHeatingTempF"
    )

    model_config = {"populate_by_name": True}


class SpaceTypeData(BaseModel):
    """Space type data."""

    cooling_temp: float | None = Field(default=None, alias="coolingTemp")
    equipment_load: float | None = Field(default=None, alias="equipmentLoad")
    exhaust_ach: float | None = Field(default=None, alias="exhaustAch")
    exhaust_area_req: float | None = Field(default=None, alias="exhaustAreaReq")
    ez: float | None = None
    heating_temp: float | None = Field(default=None, alias="heatingTemp")
    infiltration_ach_req: float | None = Field(default=None, alias="infiltrationAchReq")
    infiltration_area_req: float | None = Field(default=None, alias="infiltrationAreaReq")
    infiltration_lf_req: float | None = Field(default=None, alias="infiltrationLfReq")
    infiltration_use_separate_winter_reqs: bool | None = Field(
        default=None, alias="infiltrationUseSeparateWinterReqs"
    )
    infiltration_winter_ach_req: float | None = Field(
        default=None, alias="infiltrationWinterAchReq"
    )
    infiltration_winter_area_req: float | None = Field(
        default=None, alias="infiltrationWinterAreaReq"
    )
    infiltration_winter_lf_req: float | None = Field(default=None, alias="infiltrationWinterLfReq")
    lighting_ceiling_load_percent: float | None = Field(
        default=None, alias="lightingCeilingLoadPercent"
    )
    lighting_load: float | None = Field(default=None, alias="lightingLoad")
    name: str | None = None
    name_synonyms: list[str] | None = Field(default=None, alias="nameSynonyms")
    nc: float | None = None
    outside_ach: float | None = Field(default=None, alias="outsideAch")
    people_density: float | None = Field(default=None, alias="peopleDensity")
    people_latent_load: float | None = Field(default=None, alias="peopleLatentLoad")
    people_sensible_load: float | None = Field(default=None, alias="peopleSensibleLoad")
    register_spec: dict[FlowType, RegisterSpecConstraints] | None = Field(
        default=None, alias="registerSpec"
    )
    relative_humidity: float | None = Field(default=None, alias="relativeHumidity")
    supply_area_req: float | None = Field(default=None, alias="supplyAreaReq")
    supply_req: float | None = Field(default=None, alias="supplyReq")
    temperature_range: float | None = Field(default=None, alias="temperatureRange")
    timestamp: float | None = None
    unit_exhaust_rate: float | None = Field(default=None, alias="unitExhaustRate")
    usage_schedule: list[float] | None = Field(default=None, alias="usageSchedule")
    ventilation_area_req: float | None = Field(default=None, alias="ventilationAreaReq")
    ventilation_people_req: float | None = Field(default=None, alias="ventilationPeopleReq")

    model_config = {"populate_by_name": True}


class WallTypeData(BaseModel):
    """Wall type data."""

    ashrae_wall_type_id: str | None = Field(default=None, alias="ashraeWallTypeId")
    below_grade_cooling_temp_f: float | None = Field(default=None, alias="belowGradeCoolingTempF")
    below_grade_heating_temp_f: float | None = Field(default=None, alias="belowGradeHeatingTempF")
    color: str | None = None
    name: str | None = None
    surface_absorptance: float | None = Field(default=None, alias="surfaceAbsorptance")
    timestamp: float | None = None
    u_value: float | None = Field(default=None, alias="uValue")

    model_config = {"populate_by_name": True}


class WindowTypeData(BaseModel):
    """Window type data."""

    ashrae_window_type_id: str | None = Field(default=None, alias="ashraeWindowTypeId")
    infiltration_area_req: float | None = Field(default=None, alias="infiltrationAreaReq")
    infiltration_lf_req: float | None = Field(default=None, alias="infiltrationLfReq")
    infiltration_use_separate_winter_reqs: bool | None = Field(
        default=None, alias="infiltrationUseSeparateWinterReqs"
    )
    infiltration_winter_area_req: float | None = Field(
        default=None, alias="infiltrationWinterAreaReq"
    )
    infiltration_winter_lf_req: float | None = Field(default=None, alias="infiltrationWinterLfReq")
    name: str | None = None
    shgc: float | None = None
    timestamp: float | None = None
    u_value: float | None = Field(default=None, alias="uValue")

    model_config = {"populate_by_name": True}


# Main project data
class ProjectData(BaseModel):
    """Project data."""

    # Core fields
    address: str | None = None
    airflow_increment: int | None = Field(default=None, alias="airflowIncrement", ge=1)
    api_created: bool | None = Field(default=None, alias="apiCreated")
    building: BuildingData | None = None
    constraints: dict[str, Constraint] | None = None
    construction_type: Literal["New", "Retrofit"] | None = Field(
        default=None, alias="constructionType"
    )
    contacts: dict[str, Contact] | None = None
    description: str | None = None
    dry_side: DrySideData | None = Field(default=None, alias="drySide")
    elevation: float | None = None
    equipment_modes: dict[str, EquipmentMode] = Field(alias="equipmentModes")
    is_healthcare: bool | None = Field(default=None, alias="isHealthcare")
    is_open: bool | None = Field(default=None, alias="isOpen")
    is_template: bool | None = Field(default=None, alias="isTemplate")
    last_open_time: float | None = Field(default=None, alias="lastOpenTime")
    latitude: float | None = None
    longitude: float | None = None
    maps: dict[str, MapSpec] | None = None
    name: str
    number: str | None = None
    picture_thumbnail_url: str | None = Field(default=None, alias="pictureThumbnailURL")
    picture_url: str | None = Field(default=None, alias="pictureURL")
    picture_vertical_position: float | None = Field(default=None, alias="pictureVerticalPosition")
    project_type: ProjectType | None = Field(default=None, alias="projectType")
    revision: str | None = None
    revisions: dict[str, Revision] | None = None
    sheet_markers: dict[str, Point] | None = Field(default=None, alias="sheetMarkers")
    standards: dict[str, Standard] | None = None
    status: Literal["new", "inProgress", "inReview", "done", "archived"] | None = None
    timestamp: float | None = None
    unit_system: DisplayUnitSystemId | None = Field(default=None, alias="unitSystem")
    users: dict[str, ProjectUserData]
    ventilation_standard: VentilationStandard | None = Field(
        default=None, alias="ventilationStandard"
    )
    weather_spec: WeatherSpec | None = Field(default=None, alias="weatherSpec")
    year_built: str | None = Field(default=None, alias="yearBuilt")

    model_config = {"populate_by_name": True}


class Project(ProjectData):
    """A project with ID."""

    id: str


class ProjectSubcollections(BaseModel):
    """Project subcollections."""

    branch_types: dict[str, BranchTypeData] | None = Field(default=None, alias="branchTypes")
    deadlines: dict[str, DeadlineData] | None = None
    door_types: dict[str, DoorTypeData] | None = Field(default=None, alias="doorTypes")
    duct_types: dict[str, DuctTypeData] | None = Field(default=None, alias="ductTypes")
    graph: Graph | None = None
    pipe_types: dict[str, PipeTypeData] | None = Field(default=None, alias="pipeTypes")
    register_types: dict[str, RegisterTypeData] | None = Field(default=None, alias="registerTypes")
    reports: dict[str, APIReport] | None = None
    roof_types: dict[str, RoofTypeData] | None = Field(default=None, alias="roofTypes")
    sheet_files: dict[str, SheetFileData] | None = Field(default=None, alias="sheetFiles")
    sheets: dict[str, SheetData] | None = None
    slab_types: dict[str, SlabTypeData] | None = Field(default=None, alias="slabTypes")
    space_types: dict[str, SpaceTypeData] | None = Field(default=None, alias="spaceTypes")
    spaces: dict[str, SpaceData] | None = None
    systems: dict[str, SystemData] | None = None
    wall_types: dict[str, WallTypeData] | None = Field(default=None, alias="wallTypes")
    window_types: dict[str, WindowTypeData] | None = Field(default=None, alias="windowTypes")
    zones: dict[str, ZoneData] | None = None

    model_config = {"populate_by_name": True}


class WritableProjectSubcollections(BaseModel):
    """Project subcollections accepted by create and update requests."""

    branch_types: dict[str, BranchTypeData] | None = Field(default=None, alias="branchTypes")
    deadlines: dict[str, DeadlineData] | None = None
    door_types: dict[str, DoorTypeData] | None = Field(default=None, alias="doorTypes")
    duct_types: dict[str, DuctTypeData] | None = Field(default=None, alias="ductTypes")
    graph: Graph | None = None
    pipe_types: dict[str, PipeTypeData] | None = Field(default=None, alias="pipeTypes")
    register_types: dict[str, RegisterTypeData] | None = Field(default=None, alias="registerTypes")
    roof_types: dict[str, RoofTypeData] | None = Field(default=None, alias="roofTypes")
    sheet_files: dict[str, SheetFileData] | None = Field(default=None, alias="sheetFiles")
    sheets: dict[str, SheetData] | None = None
    slab_types: dict[str, SlabTypeData] | None = Field(default=None, alias="slabTypes")
    space_types: dict[str, SpaceTypeData] | None = Field(default=None, alias="spaceTypes")
    spaces: dict[str, SpaceData] | None = None
    systems: dict[str, SystemData] | None = None
    wall_types: dict[str, WallTypeData] | None = Field(default=None, alias="wallTypes")
    window_types: dict[str, WindowTypeData] | None = Field(default=None, alias="windowTypes")
    zones: dict[str, ZoneData] | None = None

    model_config = {"populate_by_name": True}


class ExpandedProject(ProjectData, ProjectSubcollections):
    """A project with all subcollections expanded."""

    id: str


class ProjectPost(BaseModel):
    """Data for creating a new project."""

    # Optional because project can be created with default name
    name: str | None = None
    # All other ProjectData fields are optional for POST
    address: str | None = None
    airflow_increment: int | None = Field(default=None, alias="airflowIncrement", ge=1)
    api_created: bool | None = Field(default=None, alias="apiCreated")
    building: BuildingData | None = None
    constraints: dict[str, Constraint] | None = None
    construction_type: Literal["New", "Retrofit"] | None = Field(
        default=None, alias="constructionType"
    )
    contacts: dict[str, Contact] | None = None
    description: str | None = None
    dry_side: DrySideData | None = Field(default=None, alias="drySide")
    equipment_modes: dict[str, EquipmentMode] | None = Field(default=None, alias="equipmentModes")
    elevation: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    maps: dict[str, MapSpec] | None = None
    number: str | None = None
    project_type: ProjectType | None = Field(default=None, alias="projectType")
    status: Literal["new", "inProgress", "inReview", "done", "archived"] | None = None
    unit_system: DisplayUnitSystemId | None = Field(default=None, alias="unitSystem")
    ventilation_standard: VentilationStandard | None = Field(
        default=None, alias="ventilationStandard"
    )
    weather_spec: WeatherSpec | None = Field(default=None, alias="weatherSpec")
    year_built: str | None = Field(default=None, alias="yearBuilt")

    model_config = {"populate_by_name": True}


class ExpandedProjectPost(ProjectPost, WritableProjectSubcollections):
    """Data for creating a new expanded project."""

    pass


class ExpandedProjectPatch(BaseModel):
    """Data for updating an expanded project. All fields are optional."""

    # All fields from ExpandedProject but optional
    name: str | None = None
    address: str | None = None
    airflow_increment: int | None = Field(default=None, alias="airflowIncrement", ge=1)
    building: BuildingData | None = None
    constraints: dict[str, Constraint] | None = None
    construction_type: Literal["New", "Retrofit"] | None = Field(
        default=None, alias="constructionType"
    )
    contacts: dict[str, Contact] | None = None
    description: str | None = None
    dry_side: DrySideData | None = Field(default=None, alias="drySide")
    equipment_modes: dict[str, EquipmentMode] | None = Field(default=None, alias="equipmentModes")
    elevation: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    maps: dict[str, MapSpec] | None = None
    number: str | None = None
    project_type: ProjectType | None = Field(default=None, alias="projectType")
    status: Literal["new", "inProgress", "inReview", "done", "archived"] | None = None
    unit_system: DisplayUnitSystemId | None = Field(default=None, alias="unitSystem")
    ventilation_standard: VentilationStandard | None = Field(
        default=None, alias="ventilationStandard"
    )
    weather_spec: WeatherSpec | None = Field(default=None, alias="weatherSpec")
    year_built: str | None = Field(default=None, alias="yearBuilt")
    # Subcollections
    branch_types: dict[str, BranchTypeData] | None = Field(default=None, alias="branchTypes")
    deadlines: dict[str, DeadlineData] | None = None
    door_types: dict[str, DoorTypeData] | None = Field(default=None, alias="doorTypes")
    duct_types: dict[str, DuctTypeData] | None = Field(default=None, alias="ductTypes")
    graph: Graph | None = None
    pipe_types: dict[str, PipeTypeData] | None = Field(default=None, alias="pipeTypes")
    register_types: dict[str, RegisterTypeData] | None = Field(default=None, alias="registerTypes")
    roof_types: dict[str, RoofTypeData] | None = Field(default=None, alias="roofTypes")
    sheet_files: dict[str, SheetFileData] | None = Field(default=None, alias="sheetFiles")
    sheets: dict[str, SheetData] | None = None
    slab_types: dict[str, SlabTypeData] | None = Field(default=None, alias="slabTypes")
    space_types: dict[str, SpaceTypeData] | None = Field(default=None, alias="spaceTypes")
    spaces: dict[str, SpaceData] | None = None
    systems: dict[str, SystemData] | None = None
    wall_types: dict[str, WallTypeData] | None = Field(default=None, alias="wallTypes")
    window_types: dict[str, WindowTypeData] | None = Field(default=None, alias="windowTypes")
    zones: dict[str, ZoneData] | None = None

    model_config = {"populate_by_name": True}
