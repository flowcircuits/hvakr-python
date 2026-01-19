"""Revit data schema definitions."""

from pydantic import BaseModel, Field


class RevitBoundarySegment(BaseModel):
    """A boundary segment from Revit.

    All measurements are stored in feet.
    """

    x1: float
    x2: float
    y1: float
    y2: float


class RevitSpaceData(BaseModel):
    """Space data imported from Revit."""

    area: float
    """Area stored in square feet."""

    boundaries: list[list[RevitBoundarySegment]]
    """Nested array because Revit spaces support holes."""

    level_elevation: float = Field(alias="levelElevation")
    """Elevation stored in feet."""

    name: str | None
    number: str | None

    unbounded_height: float = Field(alias="unboundedHeight")
    """Height stored in feet."""

    unique_id: str = Field(alias="uniqueId")

    volume: float
    """Volume stored in cubic feet."""

    model_config = {"populate_by_name": True}


class RevitData(BaseModel):
    """Project data imported from Revit."""

    project_address: str | None = Field(alias="projectAddress")
    project_name: str | None = Field(alias="projectName")

    project_rotation_degrees: float = Field(alias="projectRotationDegrees")
    """Rotation stored in degrees."""

    revit_spaces: list[RevitSpaceData] = Field(alias="revitSpaces")

    model_config = {"populate_by_name": True}
