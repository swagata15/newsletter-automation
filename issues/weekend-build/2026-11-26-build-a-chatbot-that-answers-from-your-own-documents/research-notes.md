# Research notes: Build a RAG chatbot over your own documents
Checked 2026-11-05 against the official docs and installed packages.

## Search result content blocks (https://platform.claude.com/docs/en/build-with-claude/search-results)
- "Search result content blocks let Claude cite your own content the same way it cites web search results: each citation carries the source and title you provided."
- Block: {"type": "search_result", "source": ..., "title": ..., "content": [{"type": "text", "text": ...}], "citations": {"enabled": true}}
- Can be sent directly in user messages ("As top-level content: You provide search results directly in user messages for pre-fetched or cached content").
- "Citations are all-or-nothing: either all search results in a request must have citations enabled, or all must have them disabled"
- Citations come back as type search_result_location with source, title, cited_text (anthropic 2.5.0 SDK: CitationsSearchResultLocation).

## rank-bm25 (https://github.com/dorianbrown/rank_bm25), version 0.2.2 on PyPI
- BM25Okapi gives zero IDF to a term that appears in half the documents, so tiny collections (2-3 files) can return no results; BM25Plus avoids this.

## Pricing (https://platform.claude.com/docs/en/about-claude/pricing)
- Claude Sonnet 5.5: $2 / MTok input, $10 / MTok output.

## Tested
- askdocs.py with anthropic 2.5.0 and rank-bm25 0.2.2 against a simulated API: chunking, BM25 search, search_result blocks with
  citations enabled, citation converted to footnote [1] with source path, and the no-results path.
