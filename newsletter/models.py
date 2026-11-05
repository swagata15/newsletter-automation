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


class Stat(BaseModel):
    value: str = Field(description="The headline figure exactly as it should appear, e.g. '41%', '1 in 3', '2.4x', '981'")
    label: str = Field(description="What the figure means, one short sentence (max ~12 words)")


class TimelineItem(BaseModel):
    when: str = Field(description="Short time label, e.g. 'Mon', 'Nov 3', 'Saturday AM'")
    title: str = Field(description="What happened / what you do, max ~8 words")
    detail: str = Field(description="One short supporting sentence, or empty string")


VisualKind = Literal["image", "photo", "chart", "diagram", "stat", "waffle", "quote", "timeline"]


class Visual(BaseModel):
    id: str = Field(description="Placeholder id used in the markdown, e.g. 'v1'")
    kind: VisualKind
    caption: str = Field(description="One plain sentence shown under the visual")
    source_url: str = Field(
        description="image: the web page whose preview image to use. chart/stat/waffle/quote: the exact URL "
        "the numbers or words come from. photo/diagram/timeline: empty string."
    )
    source_name: str = Field(description="Credit line, e.g. 'Pew Research Center, 2024'; empty if none")
    # chart
    chart_type: Optional[Literal["bar", "hbar", "grouped_bar", "line"]] = None
    chart_title: Optional[str] = Field(default=None, description="Headline stating the finding (chart, diagram, stat, waffle, timeline)")
    y_label: Optional[str] = Field(default=None, description="Chart subtitle: what is measured and the unit")
    unit: Optional[str] = Field(default=None, description="Suffix for values, e.g. '%', or null")
    categories: Optional[list[str]] = None
    series: Optional[list[ChartSeries]] = None
    highlight: Optional[str] = Field(default=None, description="chart: the one category to emphasise; the rest are greyed out")
    annotation: Optional[str] = Field(default=None, description="chart: short callout note (max ~12 words) pointing at the highlighted category")
    # diagram
    nodes: Optional[list[DiagramNode]] = None
    edges: Optional[list[DiagramEdge]] = None
    # stat card (1-3 big numbers)
    stats: Optional[list[Stat]] = None
    # waffle / pictogram: share of 100 people
    waffle_value: Optional[float] = Field(default=None, description="waffle: percentage 0-100 to highlight as people out of 100")
    waffle_label: Optional[str] = Field(default=None, description="waffle: who the highlighted people are, e.g. 'say they feel lonely every week'")
    # pull quote (verbatim from a source in the notes)
    quote_text: Optional[str] = None
    quote_author: Optional[str] = Field(default=None, description="quote: 'Name, role / affiliation'")
    # timeline
    timeline: Optional[list[TimelineItem]] = None
    # photo (stock photo search)
    photo_query: Optional[str] = Field(
        default=None, description="photo: concrete, literal stock-photo search, e.g. 'teenager alone on bed looking at phone at night'"
    )


class Issue(BaseModel):
    title: str = Field(description="Headline, max ~70 characters")
    subtitle: str = Field(description="One-sentence teaser for the email preview")
    topic: str = Field(description="One-line description of the issue's topic, for the history log")
    cover_highlight: str = Field(description="2-4 consecutive words copied exactly from the title to mark with the highlighter on the cover")
    cover_photo_query: str = Field(description="Concrete, literal stock-photo search for the cover image (people, places, objects; no abstract 'AI brain' imagery)")
    markdown: str = Field(
        description="Full body in Markdown. Put each visual on its own line as [[VISUAL:<id>]]. Do not repeat the title."
    )
    visuals: list[Visual]
