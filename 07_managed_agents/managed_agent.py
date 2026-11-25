"""Lab 07: Managed Agents (beta). Anthropic hosts the loop AND a sandbox container with bash/files/code.

Compare with Labs 03-06, where YOU run the loop and the tools. Here you configure an agent once,
then start sessions and stream events. Billing = tokens + session runtime. Session history is kept
until you delete it.

    python managed_agent.py
"""
import anthropic

client = anthropic.Anthropic()

# --- One-time setup. In real projects, create these once (or with `ant apply`) and store the IDs. ---
environment = client.beta.environments.create(
    name="agent-labs-env",
    config={"type": "cloud",
            "networking": {"type": "limited", "allow_package_managers": True, "allow_mcp_servers": False}},
)
agent = client.beta.agents.create(
    name="Data Analyst",
    model="claude-opus-5-5",
    system="You are a data analyst. Work in the sandbox; show your results clearly.",
    tools=[{
        "type": "agent_toolset_20260401",                      # bash, file read/write/edit, etc.
        "default_config": {"enabled": True, "permission_policy": {"type": "auto"}},
        "configs": [{"name": "web_fetch", "enabled": False},   # no web needed for this job
                    {"name": "web_search", "enabled": False}],
    }],
)
print("agent:", agent.id, "environment:", environment.id)

# --- Every run: a session ---
session = client.beta.sessions.create(
    agent={"type": "agent", "id": agent.id, "version": agent.version},
    environment_id=environment.id,
    title="lab 07",
)
print(f"Watch it live: https://platform.claude.com/workspaces/default/sessions/{session.id}")

TASK = ("Generate 1,000 rows of fake e-commerce orders (date, product, price, qty) as CSV, "
        "then use Python to report revenue by product and the best week. Show the code you ran.")

with client.beta.sessions.events.stream(session_id=session.id) as stream:   # open the stream FIRST
    client.beta.sessions.events.send(
        session_id=session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": TASK}]}],
    )
    for event in stream:
        if event.type == "agent.message":
            for block in event.content:
                if block.type == "text":
                    print(block.text, end="", flush=True)
        elif event.type == "agent.tool_use":
            print(f"\n[sandbox tool] {event.name}")
            if event.evaluated_permission == "ask":            # auto policy couldn't decide: a human must
                ok = input("Allow this call? [y/N] ").strip().lower() == "y"
                client.beta.sessions.events.send(session_id=session.id, events=[{
                    "type": "user.tool_confirmation", "tool_use_id": event.id,
                    "result": "allow" if ok else "deny"}])
        elif event.type == "session.status_idle":
            if event.stop_reason.type != "requires_action":
                break
        elif event.type == "session.status_terminated":
            break
print("\n--- done ---")

# EXERCISES
# 1. Send a follow-up user.message in the SAME session ("now chart it"); the sandbox files are still there.
# 2. Add a custom tool to the agent and answer agent.custom_tool_use events with user.custom_tool_result.
# 3. Read the "outcomes" docs and kick off with user.define_outcome + a rubric instead of user.message.
