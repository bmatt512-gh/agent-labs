"""Lab 06: plug YOUR MCP server (Lab 05) into a Claude agent. Tools come from MCP, the loop from the SDK.

    python mcp_agent.py "Save a note called ideas with three blog post ideas about agents, then list my notes"
"""
import asyncio, sys
from pathlib import Path
from anthropic import AsyncAnthropic
from anthropic.lib.tools.mcp import async_mcp_tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(
    command=sys.executable,
    args=[str(Path(__file__).parent.parent / "05_mcp_server" / "notes_server.py")],
)

async def main(task: str) -> None:
    client = AsyncAnthropic()
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as mcp_client:
            await mcp_client.initialize()
            tools = (await mcp_client.list_tools()).tools
            print("MCP tools discovered:", [t.name for t in tools])

            runner = client.beta.messages.tool_runner(
                model="claude-opus-5-5",
                max_tokens=16000,
                tools=[async_mcp_tool(t, mcp_client) for t in tools],
                messages=[{"role": "user", "content": task}],
            )
            async for message in runner:
                for b in message.content:
                    if b.type == "tool_use":
                        print(f"[mcp tool] {b.name}({b.input})")
                    elif b.type == "text":
                        print(b.text)

if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "What notes do I have? Summarise them."))

# EXERCISES
# 1. Add the same server to Claude Code:  claude mcp add notes -- python /abs/path/notes_server.py
#    Then ask Claude Code to "use the notes server". Same server, different client: that's MCP's point.
# 2. Connect a SECOND MCP server (e.g. a filesystem or GitHub server) and merge both tool lists.
# 3. Run the server over HTTP: mcp.run("streamable-http"). Then use the API's mcp_servers + mcp_toolset
#    connector so the API calls the server directly (the server needs a public URL for this).
