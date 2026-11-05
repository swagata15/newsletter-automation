"""Research and writing instructions for each issue type."""

from __future__ import annotations

from .style import STYLE_GUIDE

VISUALS_GUIDE = """Visuals:
- Put each visual on its own line in the markdown as [[VISUAL:<id>]] and describe it in `visuals`.
- kind "image": source_url is the web page whose preview image represents the story (the article, GitHub repo page, or Hugging Face/arXiv paper page). Pick the most original source.
- kind "chart": ONLY use numbers that appear verbatim in the research notes, and set source_url to the exact page they came from. Never estimate, round creatively, combine incompatible studies in one chart, or invent data. 3 to 8 categories. Keep chart_title a plain statement of the finding (e.g. "Heavy chatbot users report more loneliness").
- kind "diagram": give nodes (short labels) and edges (arrows). 4 to 9 nodes. Set source_url and source_name to empty strings.
- Captions are one plain sentence. Every chart caption should say what the reader should notice."""

RESEARCH_SYSTEM = """You are the research desk for an AI newsletter. You search the web, open primary sources, and
produce accurate research notes for the writer. Accuracy beats coverage: if you cannot verify something
from a source you actually opened or a search result you saw, leave it out or mark it as unverified.
Always write full URLs next to every fact so the writer can cite them."""

WRITER_SYSTEM = f"""You are the writer of a Substack newsletter about AI. You turn research notes into a finished,
publish-ready issue. You only state facts that are in the notes, and you link sources inline.

{STYLE_GUIDE}

Formatting: plain Markdown only (## headings, paragraphs, bullet and numbered lists, bold, italics, links,
blockquotes, fenced code blocks). No tables, no HTML, no footnote syntax.

{VISUALS_GUIDE}"""


# ---------------------------------------------------------------- weekly roundup
def weekly_research(digest: str, cfg: dict, nl: dict, date_str: str) -> str:
    return f"""It is {date_str}. Build the shortlist for this week's "{cfg['label']}" roundup.

Here is raw data from news feeds, GitHub, Hugging Face Daily Papers and Hacker News for the past
{cfg['lookback_days']} days:

{digest}

Your job:
1. Use web search to find what the AI community on X (Twitter) has been talking about most this week
   (big launches, viral demos, debates, notable posts by well known researchers and founders). X has no
   feed here, so search for coverage of it.
2. Search for any major AI news from this week that is missing from the data above.
3. Combine everything and rank the 10 most important or most talked about items. Mix types: model and
   product launches, open source repos, research papers, and industry/policy news.
4. For each item, open the primary source when you can to confirm the details.

Output, for each of the 10 items:
- Headline and type (news / repo / paper / X discussion)
- What happened, with specific facts and numbers (2-4 sentences)
- Why it matters to {nl['audience']}
- Evidence it is trending (stars, upvotes, HN points, X coverage)
- Primary source URL
- Best page for a preview image (the article, the GitHub repo page, or the Hugging Face paper page)
- Any extra links (discussion threads, demos)"""


def weekly_write(notes: str, cfg: dict, nl: dict, date_str: str) -> str:
    return f"""Write this week's "{cfg['label']}" issue of {nl['name']} for {nl['audience']}.
Date: {date_str}. Voice: {nl['voice']}.

Structure:
- A 2-3 sentence intro that names the single biggest theme of the week. No greeting clichés.
- The top {cfg['num_items']} items from the research notes, in order of importance. For each:
  - `## <number>. <specific headline>`
  - an image visual on its own line ([[VISUAL:vN]], kind "image")
  - 2 short paragraphs: what happened (concrete details), then why it matters / our take
  - a final line: `**Source:** [name](url)` plus any useful extra link
- `## Also worth a look`: 3-5 one-line bullets with links for the runners up.
- A one-line sign-off.

If the notes include solid numbers that compare items (e.g. GitHub stars, benchmark scores from one
source), you may add ONE chart; otherwise images only.

Research notes:
{notes}"""


# ---------------------------------------------------------------- psychology deep dive
def psychology_research(topic: str, date_str: str) -> str:
    return f"""It is {date_str}. Prepare the evidence base for a deeply researched, data-driven newsletter article on:

"{topic}"

Do a proper literature review:
1. Find peer-reviewed studies, meta-analyses, randomised trials and large surveys (e.g. from journals, arXiv/
   PsyArXiv preprints, MIT Media Lab, OpenAI/Anthropic research, Pew Research, Gallup, APA, WHO, OECD,
   Common Sense Media). Prefer the last 3 years, but include foundational older work if it matters.
2. Open each important source (paper page, PDF or official report) and pull the exact figures.
3. Look for evidence on BOTH sides. Note where studies disagree and why (sample, method, definitions).

Output:
A. Up to 15 sources. For each: full citation (authors, year, title, journal or publisher), URL (DOI link
   if available), study design and sample size, key quantitative findings with exact numbers and
   units as stated in the source, and main limitations.
B. 3-5 chart-ready datasets: a short title, the exact numbers (categories and values, with units), and
   the exact source URL. Only numbers you saw in the source. Each dataset must come from a single source.
C. The 5 strongest, most surprising findings.
D. Where the evidence is weak, mixed or missing.
E. Practical, evidence-based takeaways for ordinary readers."""


def psychology_write(topic: str, notes: str, cfg: dict, nl: dict, date_str: str) -> str:
    return f"""Write this week's "{cfg['label']}" issue of {nl['name']}: a deeply researched, data-driven article on
"{topic}". Audience: {nl['audience']}. Voice: {nl['voice']}. Date: {date_str}.
Length: about {cfg['target_words']} words.

This is the most rigorous issue of the week. Readers should come away knowing exactly what the evidence
says, how strong it is, and what to do about it.

Structure (adapt headings to the topic, keep them specific, not generic):
- Open with the single most striking finding, with its number and source.
- `## The short answer`: 3-4 sentences, honest about uncertainty.
- 3-4 sections walking through the evidence, each anchored on specific studies (who, how many people,
  what they found, with numbers). Explain methods in plain English (e.g. "a survey can't tell us which
  came first").
- A section on the evidence pointing the other way or the big caveats.
- `## Who is most affected` (if the evidence supports it).
- `## What this means for you`: concrete, evidence-based takeaways as a short list.
- `## How we researched this`: 2-3 sentences on the sources used.
- `## References`: numbered list, full citations with links, in the order first cited.

Citations: cite inline as ([Author et al., Year](url)) the first time, and keep it natural after that.
Every number in the article must come from the notes and be attributable to a reference.

Include 3 or 4 charts built from the chart-ready datasets (kind "chart"), placed next to the paragraph
that discusses them. Do not mix data from different studies in one chart.

Research notes:
{notes}"""


# ---------------------------------------------------------------- tutorial
def tutorial_research(topic: str, cfg: dict, date_str: str) -> str:
    return f"""It is {date_str}. Prepare research for a hands-on "{cfg['label']}" tutorial:

"{topic}"

The reader will build this over one weekend in {cfg['language']}.
1. Decide the best current approach and stack. Prefer simple, well-maintained tools; a framework-free
   version using a model provider's official SDK is often clearest. Check what is current as of today.
2. Open the official documentation for every library and API you plan to use and record the exact,
   current package names, install commands, import paths, function signatures and model names. Do not
   rely on memory for APIs; they change often.
3. Find 2-4 good references for going further (official docs, well known repos, papers).
4. Note common pitfalls and costs.

Output: the recommended architecture (components and how data flows between them), verified API
details with source URLs, a step-by-step build plan split into Saturday and Sunday, pitfalls, and
further reading links."""


def tutorial_write(topic: str, notes: str, cfg: dict, nl: dict, date_str: str) -> str:
    return f"""Write this week's "{cfg['label']}" issue of {nl['name']}: a hands-on tutorial on "{topic}".
Audience: {nl['audience']} (comfortable with basic {cfg['language']}). Voice: {nl['voice']}. Date: {date_str}.
Length: about {cfg['target_words']} words of prose plus code.

Structure:
- A short hook: what they will have built by Sunday night and why it is useful.
- `## What you'll build`: one paragraph plus an architecture diagram ([[VISUAL:...]], kind "diagram").
- `## Before you start`: prerequisites, install commands, API keys, rough cost.
- `## Saturday: ...` and `## Sunday: ...` with numbered `### Step N: ...` subsections. Each step: a sentence
  on why, then a complete code block, then what to check before moving on.
- `## Common pitfalls`
- `## Take it further`: 3-5 ideas.
- `## Resources`: linked docs and repos from the notes.

Code rules: complete, runnable, consistent across steps (same file and function names), with only the
APIs, package names and model names verified in the notes. Keep files small. Use fenced code blocks
with a language tag. Code may contain any characters it needs; the no-dash rule applies to prose only.

You may add a second diagram (e.g. the agent message flow) if it genuinely helps.

Research notes:
{notes}"""


# ---------------------------------------------------------------- topic picking
def pick_topic(kind: str, used: list[str], date_str: str) -> str:
    what = {
        "psychology": "the psychological, social or mental-health impact of AI on people, answerable with real research data",
        "tutorial": "a practical AI system a developer can build in one weekend, ideally using something trending right now",
    }[kind]
    used_list = "\n".join(f"- {u}" for u in used) or "(none)"
    return f"""It is {date_str}. Search the web for what is being discussed right now and propose ONE topic for a newsletter
issue about {what}. It must be clearly different from these past topics:
{used_list}

Reply with only the topic as a single line, phrased as an engaging headline."""


REVISE_PROMPT = """Rewrite only the sentences in this newsletter that use these stock phrases, so they read like a
human wrote them: {phrases}

Rules: keep every fact, number, link, heading, code block and [[VISUAL:...]] line exactly as is. Do not use
em dashes, en dashes or double hyphens. Change nothing else. Return the full markdown and nothing else.

{markdown}"""
