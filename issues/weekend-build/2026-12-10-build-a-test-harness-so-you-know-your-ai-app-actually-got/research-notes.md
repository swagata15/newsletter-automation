# Research notes: Build an evaluation harness to test your LLM app
Checked 2026-11-05.

## Anthropic docs: Define success criteria and build evaluations
URL: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
- "Prioritize volume over quality: More questions with slightly lower signal automated grading is better than fewer questions with high-quality human hand-graded evals."
- "When deciding which method to use to grade evals, choose the fastest, most reliable, most scalable method"
- "Code-based grading: Fastest and most reliable, extremely scalable, but also lacks nuance for more complex judgments"
- "LLM-based grading: Fast and flexible, scalable and suitable for complex judgment."
- "Human grading: Most flexible and high quality, but slow and expensive."
- Examples of code-based grading: "Exact match: output == golden_answer", "String match: key_phrase in output".

## SDK
- Structured outputs via client.messages.parse(output_format=PydanticModel) (anthropic 2.5.0).

## Pricing (https://platform.claude.com/docs/en/about-claude/pricing)
- Claude Opus 5.5: $4 / MTok input, $20 / MTok output. Claude Sonnet 5.5: $2 / MTok input, $10 / MTok output.

## Tested
- evalkit.py with anthropic 2.5.0 against a simulated API, two runs: run 1 3/3 passed (exit 0); run 2 with a regressed app
  2/3 passed, regression "leave-days" reported, exit code 1. In run 2 the simulated judge was fooled but the code check caught the wrong number.
