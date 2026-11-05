# Research notes: Build a research assistant that searches the web and cites its sources
Checked on 2026-11-05 against the official docs and the installed SDK (anthropic 2.5.0).

## Web search tool (https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)
- Tool definition: {"type": "web_search_20260209", "name": "web_search", "max_uses": N}; optional allowed_domains or blocked_domains.
- Runs on Anthropic's servers; results come back as web_search_tool_result blocks.
- Claude's text blocks carry citations of type web_search_result_location with url, title and cited_text.
- Long server-tool turns can stop with stop_reason "pause_turn"; send the assistant content back to continue.

## Web fetch tool (https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)
- Tool definition: {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": N}.
- "Claude can only fetch URLs that have previously appeared in the conversation"
- "The web fetch tool is available on the Claude API at no additional cost."
- Results come back as web_fetch_tool_result blocks with content.url.

## Pricing (https://platform.claude.com/docs/en/about-claude/pricing)
- Web search: $10 USD per 1,000 searches, plus standard token costs for search results.
- Claude Sonnet 5.5: $2 / MTok input, $10 / MTok output.

## Tested
- scout.py run end to end with anthropic 2.5.0 against a simulated API: search, pause_turn resume, page fetch,
  citation converted to footnote [1], fetched page listed, domain restriction passed, checker flags an uncited claim.
