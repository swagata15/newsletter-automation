# First batch: 11 pre-written issues

Written in a Claude Code session (no API credits used), then rendered with the same graphics engine
and fact checks as the automated pipeline:

```bash
python -m newsletter --from-json draft.json --notes notes.md --type <type> --date <YYYY-MM-DD> --dry-run
```

Each issue lands in `issues/<category>/<date>-<title>/` with status `local`. On its scheduled day the
GitHub Action finds it and posts it to Substack as a draft (re-rendering first, so photos are added if
`PEXELS_API_KEY` is set) instead of generating a new one.

## Schedule

| Date | Day | Category | Topic |
|---|---|---|---|
| 2026-11-06 | Fri | This Week in AI | The week's top 5-6 AI stories, repos and papers |
| 2026-11-10 | Tue | AI and the Mind | Is AI making us lonely? What the research on AI companions and chatbots actually shows |
| 2026-11-12 | Thu | Weekend Build | Build a multi-agent orchestration system in a weekend |
| 2026-11-17 | Tue | AI and the Mind | Does using AI make us worse at thinking? Cognitive offloading and critical thinking |
| 2026-11-19 | Thu | Weekend Build | Build a research assistant that searches the web and cites its sources |
| 2026-11-24 | Tue | AI and the Mind | AI and anxiety: how automation fears are affecting workers' mental health |
| 2026-11-26 | Thu | Weekend Build | Build a RAG chatbot over your own documents |
| 2026-12-01 | Tue | AI and the Mind | Do people trust AI more than humans? Algorithm appreciation and aversion |
| 2026-12-03 | Thu | Weekend Build | Build an AI agent that triages your inbox |
| 2026-12-08 | Tue | AI and the Mind | AI therapy chatbots: does the evidence support them? |
| 2026-12-10 | Thu | Weekend Build | Build an evaluation harness to test your LLM app |

## Rules for writing them (same as the automated prompts)

- Research from primary sources: open the paper, report or docs and take figures verbatim.
  Save them with URLs in `notes.md`; every chart, stat, pictogram and quote is checked against it.
- Follow `newsletter/prompts.py` for structure and visual mix per category, `newsletter/style.py`
  STYLE_GUIDE for voice (no em/en dashes, no stock AI phrases), and `BRAND.md` for the look.
- Weekly issues are only written for the current week (Friday's); later weeks are generated
  automatically on the day.

## Environment needed

- GitHub access to this repo (to push).
- Network access: Full (to read papers and docs, and to fetch article preview images).
- `PEXELS_API_KEY` environment variable for photos.
