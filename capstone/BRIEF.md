# Capstone: an "Inbox-to-Action" agent (build it yourself, no starter code)

Build an agent that takes a folder of messy inputs (emails as .txt, meeting notes, a CSV of tasks)
and produces a prioritised weekly plan, creating notes via YOUR MCP server from Lab 05.

Must have:
1. Hand-written loop (Lab 03 style) OR tool runner, your choice; justify it in a README.
2. At least one tool served over MCP and one local Python tool.
3. Guardrails: max turns, sandboxed paths, human approval for any write/delete.
4. Errors returned to the model as tool_result is_error, never crashing the loop.
5. Prompt caching on the system prompt + tools; log cache_read_input_tokens per turn.
6. A tiny eval: 5 input folders + what a good plan must contain; a script that scores runs.
   (An agent without an eval is a demo, not a product.)

Stretch: split into an orchestrator + a cheaper "reader" subagent (claude-haiku-5-5) that summarises
each file, then rebuild the whole thing on Managed Agents and compare cost, latency, and code size.
