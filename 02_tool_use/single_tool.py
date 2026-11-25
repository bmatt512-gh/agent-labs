"""Lab 02: tool use by hand, ONE round trip. Goal: understand tool_use -> tool_result."""
import json
import anthropic

client = anthropic.Anthropic()

tools = [{
    "name": "get_weather",
    "description": "Get the current weather for a city. Use whenever the user asks about weather.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name, e.g. Paris"}},
        "required": ["city"],
        "additionalProperties": False,
    },
    "strict": True,  # guarantees the input matches the schema
}]

def get_weather(city: str) -> str:
    fake = {"paris": "14C, rain", "tokyo": "22C, sunny"}
    return fake.get(city.lower(), "18C, cloudy")

messages = [{"role": "user", "content": "Should I bring an umbrella in Paris today?"}]
first = client.messages.create(model="claude-opus-5-5", max_tokens=16000, tools=tools, messages=messages)
print("1st stop_reason:", first.stop_reason)  # expect "tool_use"

tool_use = next(b for b in first.content if b.type == "tool_use")
print("Claude wants:", tool_use.name, json.dumps(tool_use.input))

# Append Claude's turn UNCHANGED (all blocks), then the tool result as a user turn.
messages.append({"role": "assistant", "content": first.content})
messages.append({"role": "user", "content": [{
    "type": "tool_result",
    "tool_use_id": tool_use.id,           # must match
    "content": get_weather(**tool_use.input),
}]})

second = client.messages.create(model="claude-opus-5-5", max_tokens=16000, tools=tools, messages=messages)
print("2nd stop_reason:", second.stop_reason)  # expect "end_turn"
print("".join(b.text for b in second.content if b.type == "text"))

# EXERCISES
# 1. Ask "Weather in Paris AND Tokyo?". Claude may return TWO tool_use blocks. Return both
#    tool_results in ONE user message. This script breaks on that; fix it.
# 2. Make get_weather raise for "Atlantis" and return {"is_error": True, ...}. Watch Claude recover.
# 3. Write a deliberately vague tool description. How does behaviour change? (Descriptions are prompts.)
