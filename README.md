# Agent Labs: theory to practice

Hands-on labs that follow the Claude Academy courses. Each lab is one small file with exercises at the
bottom. **Do the exercises**; that's where the learning happens.

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...     # from https://platform.claude.com -> API Keys
```
Getting a key: sign up at platform.claude.com, add a small amount of credit (US$5 covers every lab
here many times over), then create a key. Never commit it.

## The path

| Lab | You learn | Needs key |
|---|---|---|
| 01_first_call | messages, stop_reason, usage, statelessness | yes |
| 02_tool_use | tool schema -> tool_use -> tool_result, by hand | yes |
| **03_agent_loop** | **the agentic loop itself + guardrails + human approval** | yes |
| 04_tool_runner | let the SDK run the loop | yes |
| 05_mcp_server | build an MCP server (tools, resources, prompts) | **no**: start here today |
| 06_mcp_client_agent | Claude agent using your MCP server | yes |
| 07_managed_agents | Anthropic-hosted loop + sandbox (beta) | yes |
| capstone | design one end to end, with an eval | yes |

Start with **Lab 05** (`cd 05_mcp_server && python test_server.py`): it runs with no key.
Then add it to Claude Code (`claude mcp add notes -- python $(pwd)/notes_server.py`) and talk to it.

## The mental model (memorise this)
- **An agent = model + tools + a loop + guardrails.** Lab 03 is the entire idea in ~80 lines.
- **Tool descriptions are prompts.** Most agent bugs are vague tools, not bad models.
- **Return errors to the model** (`is_error: true`); it will usually recover.
- **Context is your budget.** Every turn resends history; use caching, and keep tool outputs small.
- **Start simple:** single call -> workflow (code drives) -> agent (model drives). Only climb when needed.
- **Where the loop runs:** you host it (Labs 03/04/06), Anthropic hosts it (Lab 07, Managed Agents), or
  you use the Claude Agent SDK (Claude Code as a library; see code.claude.com/docs/en/agent-sdk).
- **Evals turn you from a hobbyist into an expert.** Measure every change.

## After the labs
1. Read Anthropic's "Building effective agents" post and the tool-use docs on platform.claude.com.
2. Try the Claude Agent SDK and build the capstone again with it.
3. Learn the production topics: prompt caching, compaction / context editing, streaming,
   refusal handling (`stop_reason == "refusal"`, and the `fallbacks` parameter), cost and latency.
4. Publish an MCP server for a tool you actually use (Notion, your DB, an internal API).

Notes: these labs use `claude-opus-5-5`. On that model thinking can't be turned off, `tool_choice`
`any`/`tool` returns a 400 (use `auto` + a clear instruction), and the default effort is `medium`.
The labs use `mcp` 2.x, where `FastMCP` is now `MCPServer`, so v1 tutorials need small changes.
