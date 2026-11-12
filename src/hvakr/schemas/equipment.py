"""Equipment configuration schemas for central and terminal unit graph nodes."""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class OutsideAirMethod(str, Enum):
    """Method for calculating outside air."""

    SUM_OF_SPACES = "SUM_OF_SPACES"
    PERCENT = "PERCENT"
    CUSTOM = "CUSTOM"
    MULTI_ZONE = "MULTI_ZONE"


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


class EquipmentOutlet(BaseModel):
    """Supply duct losses after the last component."""

    # Degrees Fahrenheit delta.
    duct_heat_gain: float | None = Field(default=None, alias="ductHeatGain")
    # Decimal fraction: 0.01 is 1%.
    duct_leakage_percent: float | None = Field(default=None, alias="ductLeakagePercent")

    model_config = {"populate_by_name": True}


class EnergySchedule(BaseModel):
    """Operating schedule used for central-unit energy calculations."""

    occupied_hours: list[float] | None = Field(default=None, alias="occupiedHours")
    warmup_hours: float | None = Field(default=None, alias="warmupHours")
    warmup_multiplier: float | None = Field(default=None, alias="warmupMultiplier")

    model_config = {"populate_by_name": True}


class EquipmentEfficiency(BaseModel):
    """Central-unit heating and cooling efficiency inputs."""

    heating_type: Literal["heatPump", "gasFurnace"] | None = Field(
        default=None, alias="heatingType"
    )
    cooling_seer: float | None = Field(default=None, alias="coolingSEER")
    heating_cop: float | None = Field(default=None, alias="heatingCOP")
    heating_afue: float | None = Field(default=None, alias="heatingAFUE")

    model_config = {"populate_by_name": True}


class EnergyConfiguration(BaseModel):
    """Energy configuration of a unit."""

    schedule: EnergySchedule | None = None
    efficiency: EquipmentEfficiency | None = None


class EquipmentConfig(BaseModel):
    """Equipment configuration stored directly on central and terminal unit nodes."""

    components: list[EquipmentComponent] | None = None
    component_configs_by_mode: dict[str, dict[str, ComponentConfiguration]] | None = Field(
        default=None, alias="componentConfigsByMode"
    )
    misc_inefficiencies: float | None = Field(default=None, alias="miscInefficiencies")
    pressure_loss: float | None = Field(default=None, alias="pressureLoss")
    inlet_data: EquipmentInletData | None = Field(default=None, alias="inletData")
    outlet: EquipmentOutlet | None = None
    energy_configuration: EnergyConfiguration | None = Field(
        default=None, alias="energyConfiguration"
    )

    model_config = {"populate_by_name": True}


class EquipmentProjectScope(BaseModel):
    """The system or zone a unit node serves. Its ID is not the graph node ID."""

    type: Literal["system", "zone"]
    id: str
