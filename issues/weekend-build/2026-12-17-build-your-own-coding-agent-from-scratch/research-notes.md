# Research notes: Build a coding agent from scratch
Checked 2026-11-05 against Anthropic docs and the installed SDK (anthropic 2.5.0).

## Text editor tool (https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool)
- Declared as {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}; Anthropic-defined, schema-less, client-executed.
- Commands: view (path, optional view_range), create (path, file_text), str_replace (path, old_str, new_str: replace exactly one occurrence, error if 0 or >1), insert (path, insert_line, insert_text).
- Optional max_characters caps view output (text_editor_20250728 and later).
- Security guidance: path is untrusted model output; resolve it and confirm it stays inside the project root (e.g. Path.resolve() then is_relative_to(root)).
- Return errors as tool_result with is_error: true so Claude can recover.

## Tool use loop (https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- When stop_reason is "tool_use", run each tool_use block and send all tool_result blocks back in a single user message.
- Bash tool guidance: commands are untrusted model output; run in isolation, prefer an allowlist; a blocklist is not sufficient.

## Pricing (https://platform.claude.com/docs/en/about-claude/pricing)
- Claude Sonnet 5.5: $2 / MTok input, $10 / MTok output.

## Tested
- minicoder.py with anthropic 2.5.0 and pytest against a simulated API on a real buggy project: directory view, a path escape
  (../../../etc/passwd) refused with is_error, a test file edit refused, the bug fixed with str_replace, real pytest went from
  1 failed to 1 passed, changed files reported. 30-step cap.
