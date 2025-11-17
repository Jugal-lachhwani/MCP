import os
from mcp.server.fastmcp import FastMCP
import mcp.types as types

mcp = FastMCP("file-agent")

# Tool 1: List files in a directory
@mcp.tool()
async def list_files(path: str = ".") -> str:
    """List files in a directory.

    Args:
        path: Directory path (default is current folder).
    """
    if not os.path.exists(path):
        return f"Path not found: {path}"
    if not os.path.isdir(path):
        return f"Not a directory: {path}"

    files = os.listdir(path)
    return "\n".join(files) if files else "No files found."

# Tool 2: Read a file
@mcp.tool()
async def read_file(path: str) -> str:
    """Read and return the contents of a text file.

    Args:
        path: Path to the file.
    """
    if not os.path.exists(path):
        return f"File not found: {path}"
    if not os.path.isfile(path):
        return f"Not a file: {path}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# Tool 3: Search text in a file
@mcp.tool()
async def search_file(path: str, keyword: str) -> str:
    """Search for a keyword in a text file.

    Args:
        path: Path to the file.
        keyword: Word or phrase to search.
    """
    if not os.path.exists(path):
        return f"File not found: {path}"

    matches = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                if keyword.lower() in line.lower():
                    matches.append(f"Line {i}: {line.strip()}")
    except Exception as e:
        return f"Error searching file: {e}"

    return "\n".join(matches) if matches else f"No matches for '{keyword}'."

# Run the server
if __name__ == "__main__":
    print("Server running ...")
    mcp.run(transport="stdio")
