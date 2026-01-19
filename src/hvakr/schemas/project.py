"""Project schema definitions."""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from hvakr.schemas.common import DisplayUnitSystemId, Point, Rect
from hvakr.schemas.graph import DuctSize, FlowType, Graph


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


class OutsideAirMethod(int, Enum):
    """Method for calculating outside air."""

    SUM_OF_SPACES = 0
    PERCENT = 1
    CUSTOM = 2
    MULTI_ZONE = 3


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

    duct_sizes: dict[str, dict[str, Any]] | None = Field(default=None, alias="ductSizes")
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

    air_transfer_in: float | None = Field(default=None, alias="airTransferIn")
    air_transfer_out: float | None = Field(default=None, alias="airTransferOut")
    apply_roof_load_to_ceiling: bool | None = Field(default=None, alias="applyRoofLoadToCeiling")
    ceiling_height: float | None = Field(default=None, alias="ceilingHeight")
    custom_exhaust: float | None = Field(default=None, alias="customExhaust")
    custom_outside_airflow: float | None = Field(default=None, alias="customOutsideAirflow")
    custom_return: float | None = Field(default=None, alias="customReturn")
    custom_supply: float | None = Field(default=None, alias="customSupply")
    description: str | None = None
    edges: dict[str, Edge]
    exhaust_units: float | None = Field(default=None, alias="exhaustUnits")
    infiltration_ach_req: float | None = Field(default=None, alias="infiltrationAchReq")
    infiltration_area_req: float | None = Field(default=None, alias="infiltrationAreaReq")
    infiltration_flow_rate_req: float | None = Field(default=None, alias="infiltrationFlowRateReq")
    infiltration_lf_req: float | None = Field(default=None, alias="infiltrationLfReq")
    infiltration_req_method: InfiltrationRequirementMethod | None = Field(
        default=None, alias="infiltrationReqMethod"
    )
    infiltration_use_separate_winter_reqs: bool | None = Field(
        default=None, alias="infiltrationUseSeparateWinterReqs"
    )
    infiltration_winter_ach_req: float | None = Field(
        default=None, alias="infiltrationWinterAchReq"
    )
    infiltration_winter_area_req: float | None = Field(
        default=None, alias="infiltrationWinterAreaReq"
    )
    infiltration_winter_flow_rate_req: float | None = Field(
        default=None, alias="infiltrationWinterFlowRateReq"
    )
    infiltration_winter_lf_req: float | None = Field(
        default=None, alias="infiltrationWinterLfReq"
    )
    infiltration_winter_req_method: InfiltrationRequirementMethod | None = Field(
        default=None, alias="infiltrationWinterReqMethod"
    )
    level: int
    misc_heating_load: float | None = Field(default=None, alias="miscHeatingLoad")
    misc_latent_cooling_load: float | None = Field(default=None, alias="miscLatentCoolingLoad")
    misc_sensible_cooling_load: float | None = Field(default=None, alias="miscSensibleCoolingLoad")
    name: str | None = None
    number: str | None = None
    occupancy: float | None = None
    revit_id: str | None = Field(default=None, alias="revitId")
    roof_direction: EdgeExposure | None = Field(default=None, alias="roofDirection")
    roof_pitch: float | None = Field(default=None, alias="roofPitch")
    roof_type_id: str | None = Field(default=None, alias="roofTypeId")
    skylights: dict[str, SkylightData] | None = None
    slab_height: float | None = Field(default=None, alias="slabHeight")
    slab_type_id: str | None = Field(default=None, alias="slabTypeId")
    space_type_id: str | None = Field(default=None, alias="spaceTypeId")
    suggested_space_name: str | None = Field(default=None, alias="suggestedSpaceName")
    suggested_space_number: str | None = Field(default=None, alias="suggestedSpaceNumber")
    zone_id: str | None = Field(default=None, alias="zoneId")

    model_config = {"populate_by_name": True}


# System configuration
class SupplyAirData(BaseModel):
    """Supply air data."""

    cooling_temperature: float | None = Field(default=None, alias="coolingTemperature")
    custom_supply_in: float | None = Field(default=None, alias="customSupplyIn")
    duct_heat_gain: float | None = Field(default=None, alias="ductHeatGain")
    duct_leakage_percent: float | None = Field(default=None, alias="ductLeakagePercent")
    heating_temperature: float | None = Field(default=None, alias="heatingTemperature")

    model_config = {"populate_by_name": True}


class CoolingCoilData(BaseModel):
    """Cooling coil data."""

    chilled_water_delta_t: float | None = Field(default=None, alias="chilledWaterDeltaT")
    type: CoolingCoilType | None = None

    model_config = {"populate_by_name": True}


class HeatingCoilData(BaseModel):
    """Heating coil data."""

    heating_water_delta_t: float | None = Field(default=None, alias="heatingWaterDeltaT")
    type: HeatingCoilType | None = None

    model_config = {"populate_by_name": True}


class ReturnAirData(BaseModel):
    """Return air data."""

    duct_heat_gain: float | None = Field(default=None, alias="ductHeatGain")
    duct_leakage_percent: float | None = Field(default=None, alias="ductLeakagePercent")

    model_config = {"populate_by_name": True}


class OutsideAirData(BaseModel):
    """Outside air data."""

    custom: float | None = None
    method: OutsideAirMethod | None = None
    percentage: float | None = None
    previous_method: OutsideAirMethod | None = Field(default=None, alias="previousMethod")

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


class CentralUnitConfiguration(BaseModel):
    """Central unit configuration."""

    cooling_coil: bool | None = Field(default=None, alias="coolingCoil")
    cooling_coil_data: CoolingCoilData | None = Field(default=None, alias="coolingCoilData")
    custom_relief_air: float | None = Field(default=None, alias="customReliefAir")
    dimension_data: CentralUnitDimensionData | None = Field(default=None, alias="dimensionData")
    diversity_data: DiversityData | None = Field(default=None, alias="diversityData")
    erv_wheel: bool | None = Field(default=None, alias="ervWheel")
    erv_wheel_effectiveness: float | None = Field(default=None, alias="ervWheelEffectiveness")
    fan_motor_heat_gain: float | None = Field(default=None, alias="fanMotorHeatGain")
    heating_coil: bool | None = Field(default=None, alias="heatingCoil")
    heating_coil_data: HeatingCoilData | None = Field(default=None, alias="heatingCoilData")
    misc_inefficiencies: float | None = Field(default=None, alias="miscInefficiencies")
    outside_air: bool | None = Field(default=None, alias="outsideAir")
    outside_air_data: OutsideAirData | None = Field(default=None, alias="outsideAirData")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    return_air: bool | None = Field(default=None, alias="returnAir")
    return_air_data: ReturnAirData | None = Field(default=None, alias="returnAirData")
    supply_air_data: SupplyAirData | None = Field(default=None, alias="supplyAirData")

    model_config = {"populate_by_name": True}


class EnergyConfiguration(BaseModel):
    """Energy configuration."""

    efficiency: float | None = None
    energy_type: Literal["electric", "gas"] | None = Field(default=None, alias="energyType")
    name: str | None = None
    use_factor: float | None = Field(default=None, alias="useFactor")

    model_config = {"populate_by_name": True}


class SystemData(BaseModel):
    """System data."""

    central_unit_configuration: CentralUnitConfiguration | None = Field(
        default=None, alias="centralUnitConfiguration"
    )
    color: str | None = None
    configured: bool | None = None
    energy_configurations: dict[str, EnergyConfiguration] | None = Field(
        default=None, alias="energyConfigurations"
    )
    name: str | None = None

    model_config = {"populate_by_name": True}


# Terminal unit / Zone configuration
class TerminalUnitDimensionData(BaseModel):
    """Terminal unit dimension data."""

    inlet_size: TerminalUnitInletSize | None = Field(default=None, alias="inletSize")

    model_config = {"populate_by_name": True}


class TerminalUnitOutsideAirData(BaseModel):
    """Terminal unit outside air data."""

    custom: float | None = None
    method: TerminalUnitOutsideAirMethod | None = None
    percentage: float | None = None
    previous_method: TerminalUnitOutsideAirMethod | None = Field(
        default=None, alias="previousMethod"
    )

    model_config = {"populate_by_name": True}


class TerminalUnitSupplyAirData(BaseModel):
    """Terminal unit supply air data."""

    cooling_temperature: float | None = Field(default=None, alias="coolingTemperature")
    custom_supply_in: float | None = Field(default=None, alias="customSupplyIn")
    heating_temperature: float | None = Field(default=None, alias="heatingTemperature")

    model_config = {"populate_by_name": True}


class TerminalUnitConfiguration(BaseModel):
    """Terminal unit configuration."""

    cooling_coil: bool | None = Field(default=None, alias="coolingCoil")
    cooling_coil_data: CoolingCoilData | None = Field(default=None, alias="coolingCoilData")
    custom_return_in: float | None = Field(default=None, alias="customReturnIn")
    dimension_data: TerminalUnitDimensionData | None = Field(default=None, alias="dimensionData")
    heating_coil: bool | None = Field(default=None, alias="heatingCoil")
    heating_coil_data: HeatingCoilData | None = Field(default=None, alias="heatingCoilData")
    outside_air_data: TerminalUnitOutsideAirData | None = Field(
        default=None, alias="outsideAirData"
    )
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    return_air: bool | None = Field(default=None, alias="returnAir")
    supply_air_data: TerminalUnitSupplyAirData | None = Field(default=None, alias="supplyAirData")

    model_config = {"populate_by_name": True}


class ZoneData(BaseModel):
    """Zone data."""

    color: str | None = None
    configured: bool | None = None
    name: str | None = None
    system_id: str | None = Field(default=None, alias="systemId")
    terminal_unit_configuration: TerminalUnitConfiguration | None = Field(
        default=None, alias="terminalUnitConfiguration"
    )

    model_config = {"populate_by_name": True}


# Type data models
class BranchTypeData(BaseModel):
    """Branch type data."""

    # Add fields as needed based on schema
    pass


class DeadlineData(BaseModel):
    """Deadline data."""

    # Add fields as needed based on schema
    pass


class DoorTypeData(BaseModel):
    """Door type data."""

    # Add fields as needed based on schema
    pass


class DuctTypeData(BaseModel):
    """Duct type data."""

    # Add fields as needed based on schema
    pass


class PipeTypeData(BaseModel):
    """Pipe type data."""

    # Add fields as needed based on schema
    pass


class RegisterTypeData(BaseModel):
    """Register type data."""

    # Add fields as needed based on schema
    pass


class ReportData(BaseModel):
    """Report data."""

    # Add fields as needed based on schema
    pass


class RoofTypeData(BaseModel):
    """Roof type data."""

    # Add fields as needed based on schema
    pass


class SheetFileData(BaseModel):
    """Sheet file data."""

    # Add fields as needed based on schema
    pass


class SheetData(BaseModel):
    """Sheet data."""

    # Add fields as needed based on schema
    pass


class SlabTypeData(BaseModel):
    """Slab type data."""

    # Add fields as needed based on schema
    pass


class SpaceTypeData(BaseModel):
    """Space type data."""

    # Add fields as needed based on schema
    pass


class VersionSetData(BaseModel):
    """Version set data."""

    # Add fields as needed based on schema
    pass


class WallTypeData(BaseModel):
    """Wall type data."""

    # Add fields as needed based on schema
    pass


class WindowTypeData(BaseModel):
    """Window type data."""

    # Add fields as needed based on schema
    pass


# Main project data
class ProjectData(BaseModel):
    """Project data."""

    # Computed fields
    owner: str | None = Field(default=None, alias="_owner")
    user_emails: list[str] | None = Field(default=None, alias="_userEmails")

    # Core fields
    address: str | None = None
    api_created: bool | None = Field(default=None, alias="apiCreated")
    building: BuildingData | None = None
    constraints: dict[str, Constraint] | None = None
    construction_type: Literal["New", "Retrofit"] | None = Field(
        default=None, alias="constructionType"
    )
    contacts: dict[str, Contact] | None = None
    description: str | None = None
    dry_side: DrySideData | None = Field(default=None, alias="drySide")
    duplicated_from: str | None = Field(default=None, alias="duplicatedFrom")
    elevation: float | None = None
    from_example: str | None = Field(default=None, alias="fromExample")
    is_archived: bool | None = Field(default=None, alias="isArchived")
    is_deleted: bool | None = Field(default=None, alias="isDeleted")
    is_example: bool | None = Field(default=None, alias="isExample")
    is_hvakr_template: bool | None = Field(default=None, alias="isHVAKRTemplate")
    is_template: bool | None = Field(default=None, alias="isTemplate")
    last_open_time: float | None = Field(default=None, alias="lastOpenTime")
    latitude: float | None = None
    longitude: float | None = None
    map_spec: MapSpec | None = Field(default=None, alias="mapSpec")
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
    reports: dict[str, ReportData] | None = None
    roof_types: dict[str, RoofTypeData] | None = Field(default=None, alias="roofTypes")
    sheet_files: dict[str, SheetFileData] | None = Field(default=None, alias="sheetFiles")
    sheets: dict[str, SheetData] | None = None
    slab_types: dict[str, SlabTypeData] | None = Field(default=None, alias="slabTypes")
    space_types: dict[str, SpaceTypeData] | None = Field(default=None, alias="spaceTypes")
    spaces: dict[str, SpaceData] | None = None
    systems: dict[str, SystemData] | None = None
    version_sets: dict[str, VersionSetData] | None = Field(default=None, alias="versionSets")
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
    # Optional because project can be created with default users
    users: dict[str, ProjectUserData] | None = None
    # All other ProjectData fields are optional for POST
    address: str | None = None
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
    latitude: float | None = None
    longitude: float | None = None
    map_spec: MapSpec | None = Field(default=None, alias="mapSpec")
    number: str | None = None
    project_type: ProjectType | None = Field(default=None, alias="projectType")
    unit_system: DisplayUnitSystemId | None = Field(default=None, alias="unitSystem")
    ventilation_standard: VentilationStandard | None = Field(
        default=None, alias="ventilationStandard"
    )
    weather_spec: WeatherSpec | None = Field(default=None, alias="weatherSpec")
    year_built: str | None = Field(default=None, alias="yearBuilt")

    model_config = {"populate_by_name": True}


class ExpandedProjectPost(ProjectPost, ProjectSubcollections):
    """Data for creating a new expanded project."""

    pass


class ExpandedProjectPatch(BaseModel):
    """Data for updating an expanded project. All fields are optional."""

    # All fields from ExpandedProject but optional
    name: str | None = None
    users: dict[str, ProjectUserData] | None = None
    address: str | None = None
    building: BuildingData | None = None
    constraints: dict[str, Constraint] | None = None
    construction_type: Literal["New", "Retrofit"] | None = Field(
        default=None, alias="constructionType"
    )
    contacts: dict[str, Contact] | None = None
    description: str | None = None
    dry_side: DrySideData | None = Field(default=None, alias="drySide")
    elevation: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    map_spec: MapSpec | None = Field(default=None, alias="mapSpec")
    number: str | None = None
    project_type: ProjectType | None = Field(default=None, alias="projectType")
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
    reports: dict[str, ReportData] | None = None
    roof_types: dict[str, RoofTypeData] | None = Field(default=None, alias="roofTypes")
    sheet_files: dict[str, SheetFileData] | None = Field(default=None, alias="sheetFiles")
    sheets: dict[str, SheetData] | None = None
    slab_types: dict[str, SlabTypeData] | None = Field(default=None, alias="slabTypes")
    space_types: dict[str, SpaceTypeData] | None = Field(default=None, alias="spaceTypes")
    spaces: dict[str, SpaceData] | None = None
    systems: dict[str, SystemData] | None = None
    version_sets: dict[str, VersionSetData] | None = Field(default=None, alias="versionSets")
    wall_types: dict[str, WallTypeData] | None = Field(default=None, alias="wallTypes")
    window_types: dict[str, WindowTypeData] | None = Field(default=None, alias="windowTypes")
    zones: dict[str, ZoneData] | None = None

    model_config = {"populate_by_name": True}
