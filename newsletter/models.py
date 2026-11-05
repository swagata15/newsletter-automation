"""Structured output Claude returns for every issue."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChartSeries(BaseModel):
    name: str = Field(description="Legend label, e.g. 'Heavy users' or '2024'")
    values: list[float] = Field(description="One value per category, in the same order")


class DiagramNode(BaseModel):
    id: str
    label: str = Field(description="Short box label, max ~4 words")


class DiagramEdge(BaseModel):
    source: str = Field(description="id of the node the arrow starts at")
    target: str = Field(description="id of the node the arrow points to")
    label: str = Field(description="Optional short arrow label, or empty string")


class Visual(BaseModel):
    id: str = Field(description="Placeholder id used in the markdown, e.g. 'v1'")
    kind: Literal["image", "chart", "diagram"]
    caption: str = Field(description="One-sentence caption shown under the visual")
    source_url: str = Field(
        description="image: the web page whose preview image to use (article, repo or paper page). "
        "chart: the exact URL the numbers come from. diagram: empty string."
    )
    source_name: str = Field(description="Human name of the source for the credit line, e.g. 'Pew Research Center, 2024'")
    # chart fields
    chart_type: Optional[Literal["bar", "hbar", "grouped_bar", "line"]] = None
    chart_title: Optional[str] = None
    y_label: Optional[str] = None
    unit: Optional[str] = Field(default=None, description="Suffix for values, e.g. '%', or null")
    categories: Optional[list[str]] = None
    series: Optional[list[ChartSeries]] = None
    # diagram fields
    nodes: Optional[list[DiagramNode]] = None
    edges: Optional[list[DiagramEdge]] = None


class Issue(BaseModel):
    title: str = Field(description="Headline, max ~70 characters")
    subtitle: str = Field(description="One-sentence teaser for the email preview")
    topic: str = Field(description="One-line description of the issue's topic, for the history log")
    markdown: str = Field(
        description="Full body in Markdown. Put each visual on its own line as [[VISUAL:<id>]]. "
        "Do not repeat the title."
    )
    visuals: list[Visual]
