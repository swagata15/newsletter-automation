# Brand kit: "The Marked-Up Printout"

Every graphic in this newsletter should look like a research printout that a sharp reader went
through with a highlighter and a red pen. It's human, it's evidence-first, and it can't be mistaken
for a generic AI-made image.

The colours, fonts and devices below are built into `newsletter/visuals.py` and `config.yaml`
(`brand:`). Change them there and every future graphic follows.

## Where the idea comes from (inspiration, not imitation)

| What the best do | What we take | What we do differently |
|---|---|---|
| Economist / FT style data desks: chart titles that state the finding, grey first, colour only on what matters, a consistent frame | Headline titles, grey-first charts, one highlighted value, source line on everything | Our emphasis is a *highlighter swipe* and a *handwritten red-pen note*, not a coloured box |
| The Pudding and Our World in Data: pictograms and small multiples that make numbers feel human | Pictogram "100 people" graphics for percentages | Drawn in our ink-and-pencil palette, with the highlighter on the headline number |
| Big newsletters (Morning Brew, Lenny's, Axios): every issue instantly recognisable, recurring sections, skimmable | Named series with their own colour tab; the same cover layout every time | No emoji, no mascots, no stock "AI brain" art |
| Successful indie newsletters: pick one visual constraint and live in it | One constraint: everything is ink on newsprint, marked up by hand | |

## Colour

| Token | Hex | Use |
|---|---|---|
| Paper | `#F4EFE6` | Background of every graphic (with a faint paper grain) |
| Card | `#FBF8F2` | Boxes on diagrams, panels |
| Ink | `#161616` | Headlines, body text |
| Ink navy | `#1B3A5C` | The data colour: the value that matters |
| Pencil | `#BDB4A5` | Everything that is context, not the point |
| Graphite | `#6A645B` | Secondary text, axis labels |
| Rule | `#D9D0C1` | Gridlines, dividers |
| Highlighter | `#F5D547` | The single most important number or phrase in a graphic |
| Red pen | `#C23B22` | Handwritten notes and feedback arrows only |

Series colours: This Week in AI uses **Ink navy** `#1B3A5C`, AI and the Mind uses **Plum** `#6A3B5A`, and
Weekend Build uses **Forest** `#2E5E4E`. Each series' colour appears on its tab, cover and duotone photos.

Extra data colours, only when a chart truly needs several series: navy, teal `#3A7D7C`, ochre `#C9973B`, plum.

## Type

| Role | Font |
|---|---|
| Headlines, big numbers, quotes | **Roboto Slab** Bold |
| Labels, body | **Roboto** |
| Kickers, section tabs (caps) | **Roboto Condensed** Bold |
| Sources, dates, timestamps, code-ish labels | **Roboto Mono** |
| Margin notes (red pen only) | **Caveat** Bold |

## Signature devices

1. **Highlighter swipe**: a slightly uneven yellow stroke behind the key number or phrase. Max one per graphic.
2. **Red-pen note**: a short handwritten remark with a wobbly arrow pointing at the thing that matters. Max one per graphic.
3. **Section tab**: a coloured index tab with the series name, top left of every graphic.
4. **Duotone photos**: every photo is re-inked in the series colour on paper, so stock photos look like ours.
5. **Mono source line**: `SOURCE ·` in Roboto Mono at the bottom of every data graphic.

## Visual types

Cover · chart (bar, horizontal bar, line) · big-number stat card · pictogram (100 people) · pull quote ·
timeline · diagram · photo · source images (article previews) for news items.

## Never

Gradients, drop shadows, glowing "AI" imagery, robots, brains, emoji, orange/purple tech palettes,
3D charts, pie charts, more than one highlighter or red-pen note per graphic, made-up numbers.
