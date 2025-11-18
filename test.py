from langchain_mcp import MCPClient

client = MCPClient("http://127.0.0.1:8000")
print(client.call("add", {"x": 5, "y": 7}))
