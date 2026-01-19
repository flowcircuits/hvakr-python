"""HVAKR Python SDK - Official client for the HVAKR API.

This module provides a Python client for interacting with the HVAKR API,
which is used for HVAC load calculation and building analysis.

Example:
    Basic usage with synchronous client::

        from hvakr import HVAKRClient

        client = HVAKRClient(access_token="your-token")
        projects = client.list_projects()
        print(projects)

    Async usage::

        import asyncio
        from hvakr import AsyncHVAKRClient

        async def main():
            async with AsyncHVAKRClient(access_token="your-token") as client:
                projects = await client.list_projects()
                print(projects)

        asyncio.run(main())
"""

from hvakr.client import AsyncHVAKRClient, HVAKRClient
from hvakr.exceptions import HVAKRClientError
from hvakr.schemas import (
    # Common
    Box,
    DisplayUnitSystemId,
    Point,
    Polygon,
    Rect,
    Size,
    # Graph
    FlowType,
    Graph,
    GraphNode,
    NodeType,
    # Outputs
    APIOutputType,
    APIProjectOutputDrySideGraph,
    APIProjectOutputLoads,
    APIProjectOutputRegisterSchedule,
    # Project
    ExpandedProject,
    ExpandedProjectPatch,
    ExpandedProjectPost,
    Project,
    ProjectData,
    ProjectPost,
    # Revit
    RevitData,
    # Weather
    WeatherStationData,
)

__version__ = "0.1.0"

__all__ = [
    # Client classes
    "HVAKRClient",
    "AsyncHVAKRClient",
    # Exceptions
    "HVAKRClientError",
    # Version
    "__version__",
    # Common schemas
    "Box",
    "DisplayUnitSystemId",
    "Point",
    "Polygon",
    "Rect",
    "Size",
    # Graph schemas
    "FlowType",
    "Graph",
    "GraphNode",
    "NodeType",
    # Output schemas
    "APIOutputType",
    "APIProjectOutputDrySideGraph",
    "APIProjectOutputLoads",
    "APIProjectOutputRegisterSchedule",
    # Project schemas
    "ExpandedProject",
    "ExpandedProjectPatch",
    "ExpandedProjectPost",
    "Project",
    "ProjectData",
    "ProjectPost",
    # Revit schemas
    "RevitData",
    # Weather schemas
    "WeatherStationData",
]
