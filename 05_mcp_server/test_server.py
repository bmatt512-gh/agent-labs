"""Talk to the server as a raw MCP client - no LLM involved. This is what Claude Code does under the hood."""
import asyncio, sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).parent / "notes_server.py")])

async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])
            print(await session.call_tool("save_note", {"title": "groceries", "body": "milk, eggs, coffee"}))
            print(await session.call_tool("search_notes", {"query": "coffee"}))
            print(await session.call_tool("read_note", {"title": "nope"}))   # error path
            print(await session.read_resource("notes://index"))

asyncio.run(main())
