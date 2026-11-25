"""Lab 04: same agent as Lab 03, but the SDK runs the loop. Compare line counts.

Once you understand Lab 03, this is what you'd normally use when you host the loop yourself.
"""
from pathlib import Path
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()
WORKSPACE = Path(__file__).parent.parent / "03_agent_loop" / "workspace"

@beta_tool
def list_files() -> str:
    """List files in the user's workspace."""
    return "\n".join(p.name for p in WORKSPACE.iterdir())

@beta_tool
def read_file(name: str) -> str:
    """Read a text file from the workspace.

    Args:
        name: File name, e.g. todo.txt
    """
    p = (WORKSPACE / name).resolve()
    if not p.is_relative_to(WORKSPACE.resolve()):
        raise ValueError("path escapes the workspace")
    return p.read_text()

runner = client.beta.messages.tool_runner(
    model="claude-opus-5-5",
    max_tokens=16000,
    tools=[list_files, read_file],   # schema is generated from the signature + docstring
    messages=[{"role": "user", "content": "Summarise every decision recorded in my workspace."}],
)

for message in runner:   # one iteration per model turn
    for b in message.content:
        if b.type == "tool_use":
            print(f"[tool] {b.name}({b.input})")
        elif b.type == "text":
            print(b.text)

# EXERCISES
# 1. Add write_file with an input() approval gate inside the function.
# 2. Use runner.until_done() instead of the for-loop; when would you prefer each?
