"""Lab 03: the agentic loop, written by hand. THE most important lab - an agent is just this loop.

    while True:
        response = model(history, tools)
        if no tool calls: done
        run every tool call, append results, repeat

Run:  python agent_loop.py "Read my notes and add my action items to todo.txt"
"""
import sys
from pathlib import Path
import anthropic

client = anthropic.Anthropic()
WORKSPACE = Path(__file__).parent / "workspace"
MAX_TURNS = 15  # guardrail: never let a loop run unbounded

def safe_path(name: str) -> Path:
    p = (WORKSPACE / name).resolve()
    if not p.is_relative_to(WORKSPACE.resolve()):
        raise ValueError("path escapes the workspace")  # guardrail: sandbox the agent
    return p

def list_files() -> str:
    return "\n".join(p.name for p in WORKSPACE.iterdir()) or "(empty)"

def read_file(name: str) -> str:
    return safe_path(name).read_text()

def write_file(name: str, content: str) -> str:
    # Human-in-the-loop: risky actions need approval.
    print(f"\n--- Agent wants to write {name} ---\n{content}\n---")
    if input("Allow? [y/N] ").strip().lower() != "y":
        return "The user declined this write. Ask what they want instead."
    safe_path(name).write_text(content)
    return f"Wrote {len(content)} chars to {name}"

TOOLS = {"list_files": list_files, "read_file": read_file, "write_file": write_file}
TOOL_SCHEMAS = [
    {"name": "list_files", "description": "List files in the user's workspace.",
     "input_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "read_file", "description": "Read a text file from the workspace.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}},
                      "required": ["name"], "additionalProperties": False}},
    {"name": "write_file", "description": "Create or OVERWRITE a workspace file with the full new content.",
     "input_schema": {"type": "object",
                      "properties": {"name": {"type": "string"}, "content": {"type": "string"}},
                      "required": ["name", "content"], "additionalProperties": False}},
]
SYSTEM = "You are a personal assistant working on files in the user's workspace. Inspect files before changing them."

def run(task: str) -> None:
    messages = [{"role": "user", "content": task}]
    for turn in range(1, MAX_TURNS + 1):
        response = client.messages.create(
            model="claude-opus-5-5", max_tokens=16000, system=SYSTEM,
            tools=TOOL_SCHEMAS, messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})
        for b in response.content:
            if b.type == "text" and b.text.strip():
                print(f"\n[claude] {b.text}")

        if response.stop_reason != "tool_use":       # end_turn, max_tokens, refusal...
            print(f"\n(done after {turn} turns, stop_reason={response.stop_reason})")
            return

        results = []
        for call in (b for b in response.content if b.type == "tool_use"):
            print(f"[tool] {call.name}({call.input})")
            try:
                out, err = TOOLS[call.name](**call.input), False
            except Exception as e:                    # errors go BACK to the model, not up the stack
                out, err = f"Error: {e}", True
            results.append({"type": "tool_result", "tool_use_id": call.id, "content": out, "is_error": err})
        messages.append({"role": "user", "content": results})  # all results in ONE message
    print("Stopped: hit MAX_TURNS")

if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or "Read my meeting notes and add any action items assigned to Bob to todo.txt")

# EXERCISES
# 1. Print response.usage each turn. Notice input tokens GROW every turn - that's the cost of history.
# 2. Add a `search_files(query)` tool. Does Claude use it instead of reading everything?
# 3. Ask it to read "../../etc/passwd". Confirm the guardrail holds and Claude handles the error.
# 4. Add prompt caching: cache_control={"type": "ephemeral"} on create(); check usage.cache_read_input_tokens.
