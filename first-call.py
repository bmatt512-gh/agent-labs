"""Lab 01: one request, one response. Goal: see what a response object actually contains."""
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1000,
    system="You are a concise tutor. Answer in at most 3 sentences.",
    messages=[{"role": "user", "content": "What is an agentic loop?"}],
    output_config={"effort": "low"}
)

# Check stop_reason BEFORE you read content. You will do this in every agent you build.
print("stop_reason:", response.stop_reason)   # end_turn | max_tokens | tool_use | refusal | ...
for block in response.content:
    if block.type == "text":
        print(block.text)
print("usage:", response.usage)                # input/output tokens = what you pay for

# EXERCISES
# 1. Add a second user turn: append the assistant reply to messages and ask a follow-up.
#    (The API is stateless: YOU send the whole history every time.)
# 2. Set max_tokens=20 and watch stop_reason become "max_tokens".
# 3. Add output_config={"effort": "low"} and then "high"; compare usage.output_tokens.
