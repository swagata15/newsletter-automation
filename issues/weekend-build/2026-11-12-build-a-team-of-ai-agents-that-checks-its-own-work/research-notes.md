# Research notes: Build a multi-agent orchestration system in a weekend
Checked on 2026-11-05 against the official docs and the installed SDK.

## Anthropic Python SDK
- Package: anthropic, latest on PyPI 2.5.0 (https://pypi.org/project/anthropic/). Repo: https://github.com/anthropics/anthropic-sdk-python
- Async client: anthropic.AsyncAnthropic(); reads ANTHROPIC_API_KEY.
- Structured outputs: client.messages.parse(..., output_format=PydanticModel) returns response.parsed_output (validated). Docs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Adaptive thinking: thinking={"type": "adaptive"}; effort via output_config={"effort": "low|medium|high|xhigh|max"}.
- Claude Opus 5.5 rejects forced tool_choice ("any"/"tool"); use structured outputs to get JSON back.
- Web search server tool: {"type": "web_search_20260209", "name": "web_search", "max_uses": N}. Long server-tool turns can stop with stop_reason "pause_turn"; send the assistant content back to continue. Docs: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
- Check stop_reason "refusal" and "max_tokens" before using content.

## Pricing (https://platform.claude.com/docs/en/about-claude/pricing)
- Claude Opus 5.5: $4 / MTok input, $20 / MTok output.
- Claude Sonnet 5.5: $2 / MTok input, $10 / MTok output.
- Web search: $10 USD per 1,000 searches, plus standard token costs for search results.

## Tested
- The agent_team code (agents.py, team.py, main.py) was run end to end with anthropic 2.5.0 against a simulated API:
  planner -> 2 parallel workers (one paused web search resumed) -> writer -> critic rejects -> revision -> critic approves. 8 API calls.
