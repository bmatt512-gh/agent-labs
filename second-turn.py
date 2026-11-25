import anthropic

client = anthropic.Anthropic()
SYSTEM = "You are a concise tutor. Answer in at most 3 sentences."

# The conversation is just a Python list we keep adding to
messages = [{"role": "user", "content": "What is an agentic loop?"}]

# ---- Turn 1 ----
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    system=SYSTEM,
    messages=messages,
)
print("CLAUDE (turn 1):", "".join(b.text for b in response.content if b.type == "text"))
print("  input_tokens:", response.usage.input_tokens)

# Save Claude's reply into the history
messages.append({"role": "assistant", "content": response.content})

# Add the follow-up question
messages.append({"role": "user", "content": "Give me a real-world example of one."})

# ---- Turn 2 ----
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    system=SYSTEM,
    messages=messages,          # the SAME list, now with 3 entries
)
print("\nCLAUDE (turn 2):", "".join(b.text for b in response.content if b.type == "text"))
print("  input_tokens:", response.usage.input_tokens)