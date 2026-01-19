"""Common schema definitions for geometry and units."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class Point(BaseModel):
    """A 2D point."""

    x: float
    y: float


class Size(BaseModel):
    """A 2D size with width and height."""

    width: float
    height: float


class Rect(BaseModel):
    """A rectangle with position and size."""

    x: float
    y: float
    width: float
    height: float


Polygon = Annotated[list[Point], Field(description="A polygon defined by a list of points")]


class Box(BaseModel):
    """A bounding box defined by two corner points."""

    x1: float
    x2: float
    y1: float
    y2: float


class DisplayUnitSystemId(str, Enum):
    """Unit system for display purposes."""

    IMPERIAL = "IMPERIAL"
    METRIC = "METRIC"
