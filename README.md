# AI Newsletter → Substack automation

Every week this pipeline:

1. **Collects** the latest AI news from RSS feeds (`config.yaml`).
2. **Writes** a full issue with Claude — picks the stories that matter, explains why, links every source.
3. **Posts** it to your Substack as a **draft** (default) for you to review, or publishes and emails subscribers directly.

It runs automatically on GitHub Actions every Monday, or on demand.

## Setup

### 1. Get your credentials

- **Claude API key** — from <https://platform.claude.com>.
- **Substack publication URL** — e.g. `https://yourname.substack.com`.
- **Substack cookie** (recommended over password, which often triggers a captcha on servers):
  1. Log in to substack.com in your browser.
  2. Open DevTools → Application (Chrome) / Storage (Firefox) → Cookies → `https://substack.com`.
  3. Copy the value of `substack.sid`. Your secret is `substack.sid=<that value>`.
  4. The cookie expires eventually — if runs start failing with auth errors, repeat this.

### 2. Run locally (optional, to try it out)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in the values
python -m newsletter --dry-run   # writes output/YYYY-MM-DD.md, doesn't touch Substack
python -m newsletter             # creates a Substack draft
```

### 3. Automate with GitHub Actions

In your repo: **Settings → Secrets and variables → Actions → New repository secret**, add:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Claude API key |
| `SUBSTACK_PUBLICATION_URL` | `https://yourname.substack.com` |
| `SUBSTACK_COOKIES` | `substack.sid=...` |

Optional: under the **Variables** tab, set `PUBLISH_MODE` to `publish` to skip the review step and send automatically.

Then go to **Actions → Weekly AI newsletter → Run workflow** to test it. After that it runs every Monday
(edit the `cron` line in `.github/workflows/newsletter.yml` to change the schedule).

## Customising

Everything editorial lives in `config.yaml`: newsletter name, audience, tone, sections, number of
stories, lookback window, tags and the list of feeds. The writing instructions are in
`newsletter/write.py` (`SYSTEM_PROMPT`).

## Notes

- Substack has no official public API. Posting uses the community
  [`python-substack`](https://github.com/ma2za/python-substack) library, which calls the same endpoints
  as the Substack editor. If Substack changes those, upgrade the library.
- Draft mode is the default on purpose: AI-written content is worth a quick human read before it goes
  to your subscribers.
- Each issue is also saved to `output/` (and as a workflow artifact on GitHub).
