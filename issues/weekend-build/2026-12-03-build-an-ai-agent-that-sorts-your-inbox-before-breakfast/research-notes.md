# Research notes: Build an AI agent that triages your inbox
Checked 2026-11-05.

## Gmail app passwords (https://support.google.com/accounts/answer/185833)
- "App passwords aren't recommended and are unnecessary in most cases." Google recommends "Sign in with Google" where available.
- "An app password is a 16-digit passcode that gives a less secure app or device permission to access your Google Account."
- "App passwords can only be used with accounts that have 2-Step Verification turned on."
- Option may be missing for work/school accounts, security-key-only 2SV, or Advanced Protection.

## Python standard library
- imaplib.IMAP4_SSL; select(mailbox, readonly=True); fetch with BODY.PEEK[] does not set the \Seen flag.
- email.message_from_bytes(..., policy=email.policy.default); msg.get_body(preferencelist=("plain", "html")).

## Claude
- Structured outputs via client.messages.parse(output_format=PydanticModel) -> response.parsed_output.
- Pricing (https://platform.claude.com/docs/en/about-claude/pricing): Claude Haiku 5.5 "For high-volume, latency-sensitive tasks such as classification, extraction, and routing", $0.10 / MTok input (prompts up to 100,000 tokens), $0.50 / MTok output.

## Tested
- sorted_inbox.py with anthropic 2.5.0 against a fake IMAP server and simulated API: read-only select, BODY.PEEK fetch,
  structured triage on claude-haiku-5-5, digest grouped by category with reply drafts, prompt-injection email filed as a newsletter.
