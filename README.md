# AI Newsletter → Substack automation

Three researched, illustrated issues a week, written by Claude and posted to your Substack.

| Day (UTC) | Issue | What it is |
|---|---|---|
| **Tuesday** | **AI and the Mind** | A deeply researched, data-driven piece on the psychological impact of AI (e.g. "Is AI making us lonely?"). Literature review of studies, surveys and meta-analyses, exact figures, 3-4 charts, numbered references. |
| **Thursday** | **Weekend Build** | A hands-on tutorial (e.g. "Build a multi-agent orchestration system in a weekend"): architecture diagram, Saturday/Sunday steps, complete code checked against current docs. |
| **Friday** | **This Week in AI** | The top 5-6 things that happened: launches, trending GitHub repos, hot papers, what AI people on X are talking about, each with an image and sources. |

## How it works

1. **Research.** Claude searches the web and opens primary sources (papers, docs, articles). The Friday
   roundup also pulls in news RSS feeds, the most starred new AI repos on GitHub, Hugging Face Daily
   Papers and top Hacker News stories. X has no free API, so X buzz is found through web search.
2. **Write.** Claude writes the issue from the research notes only, citing sources inline.
3. **De-slop.** All em dashes, en dashes and `--` are removed from the prose automatically (code is left
   alone), and stock AI phrases ("delve", "landscape", "it's not just X, it's Y", ...) trigger a rewrite of
   those sentences. The banned list is in `newsletter/style.py`.
4. **Visuals**, in our own house style, "the marked-up printout" (see [BRAND.md](BRAND.md)):
   newsprint paper, grey-first data, a highlighter swipe on the key number, handwritten red-pen notes,
   a coloured tab per series, and duotone photos. Types: cover, big-number stat cards, charts with
   highlights and margin notes, 100-people pictograms, pull quotes, timelines, diagrams, real photos
   (Pexels) and source preview images. Every number and quote in a graphic is checked against the
   research notes; anything that can't be traced is dropped automatically.
5. **Post.** Images are uploaded to Substack and the issue is saved as a **draft** for you to review
   (or published directly if you choose).

Every issue is saved in the repo, sorted by category, and listed in [`issues/README.md`](issues/README.md)
with its status (`local`, `draft`, `published`):

```
issues/
  this-week-in-ai/2026-11-07-<title>/
  ai-and-the-mind/2026-11-04-<title>/
  weekend-build/2026-11-06-<title>/
     issue.md  issue.json  research-notes.md  cover.png  v1.png ...
```

## Setup

### 1. Credentials

- **Claude API key**: from <https://platform.claude.com>.
- **Substack publication URL**: e.g. `https://yourname.substack.com`.
- **Substack cookie** (recommended over a password, which often hits a captcha on servers):
  log in to substack.com, open DevTools → Application → Cookies → `https://substack.com`, copy the
  value of `substack.sid`. The secret is `substack.sid=<value>`. Repeat if it expires.

### 2. GitHub Actions

Repo **Settings → Secrets and variables → Actions**, add these secrets:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Claude API key |
| `SUBSTACK_PUBLICATION_URL` | `https://yourname.substack.com` |
| `SUBSTACK_COOKIES` | `substack.sid=...` |
| `PEXELS_API_KEY` | optional, for real photos ([free key](https://www.pexels.com/api/)) |

Optional: a `PUBLISH_MODE` variable set to `publish` to skip the draft review.

Test it: **Actions → AI newsletter → Run workflow**, pick a type. After that it runs on schedule.
For a bulk batch, pick `all` (or one category) and set **count**; each issue becomes a Substack draft
and is committed under `issues/`.

### 3. Run locally (optional)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # fill in values
python -m newsletter --type psychology --dry-run      # writes output/, doesn't touch Substack
python -m newsletter --type tutorial --topic "Build a voice agent in a weekend"
python -m newsletter                                  # today's scheduled type, as a Substack draft
python -m newsletter --type psychology --count 3      # bulk: next 3 topics from the backlog
python -m newsletter --type all --count 2 --dry-run   # bulk: 2 per category, saved locally only
```

## Customising

`config.yaml` holds everything editorial: name, audience, voice, brand colour, which day gets which
issue, research depth per issue, word counts, tags, RSS feeds, and **topic backlogs** for the
psychology and tutorial issues. Topics are used in order and recorded in `history.json`; when a
backlog runs out, Claude proposes a fresh topic that hasn't been covered. Prompts live in
`newsletter/prompts.py`.

## Notes

- **Cost:** each issue makes a few long Claude calls with web search. Expect roughly $1-5 per issue,
  the psychology deep dive being the most expensive. Lower `max_searches` / `max_fetches` / `effort`
  in `config.yaml` to cut it.
- **Review drafts.** The pipeline only uses facts from sources it read and checks chart numbers, but
  read the draft and spot-check key figures against the linked sources before sending, especially
  for the psychology issue.
- **Images from other sites** are credited, but rights vary by publisher. Swap any you're unsure about
  in the Substack editor.
- Substack has no official API. Posting uses the community
  [`python-substack`](https://github.com/ma2za/python-substack) library; upgrade it if Substack changes.
