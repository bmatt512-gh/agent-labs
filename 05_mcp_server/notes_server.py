"""Lab 05: build an MCP server. Runs with NO API key - MCP is just a protocol for exposing tools.

Any MCP client (Claude Code, Claude Desktop, your own agent in Lab 06) can use these tools.
Note: this is the mcp 2.x API. FastMCP was renamed to MCPServer, so most v1 tutorials need translating.

    python notes_server.py            # speaks MCP over stdio (a client launches it)
    python test_server.py             # drives it with a plain MCP client
"""
from pathlib import Path
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError  # message reaches the model; plain exceptions are hidden

NOTES = Path(__file__).parent / "notes"
NOTES.mkdir(exist_ok=True)

mcp = MCPServer("notes", instructions="A personal notes store. Search before creating duplicates.")

@mcp.tool()
def list_notes() -> list[str]:
    """List the titles of all saved notes."""
    return sorted(p.stem for p in NOTES.glob("*.md"))

@mcp.tool()
def search_notes(query: str) -> list[str]:
    """Return titles of notes whose text contains the query (case-insensitive)."""
    q = query.lower()
    return [p.stem for p in NOTES.glob("*.md") if q in p.read_text().lower()]

@mcp.tool()
def read_note(title: str) -> str:
    """Read one note by its exact title."""
    path = NOTES / f"{title}.md"
    if not path.exists():
        raise ToolError(f"No note titled {title!r}. Call list_notes to see titles.")
    return path.read_text()

@mcp.tool()
def save_note(title: str, body: str) -> str:
    """Create or overwrite a note. Titles may use letters, digits, spaces, - and _."""
    if not title or not all(c.isalnum() or c in " -_" for c in title):
        raise ToolError("Invalid title")
    (NOTES / f"{title}.md").write_text(body)
    return f"Saved {title!r}"

@mcp.resource("notes://index", mime_type="text/plain")
def index() -> str:
    """A resource is read-only context the CLIENT chooses to load (vs. a tool the MODEL calls)."""
    return "\n".join(list_notes()) or "(no notes)"

@mcp.prompt()
def weekly_review() -> str:
    """A prompt is a reusable template the USER picks (e.g. a slash command in Claude Code)."""
    return "Read all my notes and write a 'Weekly review' note: wins, open loops, next steps."

if __name__ == "__main__":
    mcp.run()  # stdio transport by default; try mcp.run("streamable-http") for a remote server
