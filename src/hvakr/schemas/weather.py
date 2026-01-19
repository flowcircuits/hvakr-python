"""Weather station schema definitions."""

from enum import Enum

from pydantic import BaseModel, Field


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


class MonthlyBulbTemps(BaseModel):
    """Monthly dry-bulb and wet-bulb temperatures."""

    db: list[float]
    wb: list[float]


class WeatherStationData(BaseModel):
    """Weather station data including climate information."""

    average_daily_temperature: list[float] = Field(alias="averageDailyTemperature")
    cdd50: list[float]
    cdd65: list[float]
    cdh74: list[float]
    cdh80: list[float]
    climate_zone: str = Field(alias="climateZone")
    db_range: list[float] = Field(alias="dbRange")
    db_temp_by_heating_percent: dict[HeatingPercent, float] = Field(alias="dbTempByHeatingPercent")
    elevation: float
    hdd50: list[float]
    hdd65: list[float]
    latitude: float
    longitude: float
    monthly_bulb_temps_by_cooling_percent: dict[CoolingPercent, MonthlyBulbTemps] = Field(
        alias="monthlyBulbTempsByCoolingPercent"
    )
    station: str
    std_dev_daily_temperature: list[float] = Field(alias="stdDevDailyTemperature")
    taub: list[float]
    taud: list[float]
    timezone_offset: float = Field(alias="timezoneOffset")
    wb_range: list[float] = Field(alias="wbRange")

    model_config = {"populate_by_name": True}
