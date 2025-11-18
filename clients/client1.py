import asyncio
import sys
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import json

load_dotenv()

PYTHON = sys.executable

# MCP servers
SERVERS = {
    "math": {
        "transport": "stdio",
        "command": PYTHON,
        "args": ["-u", r"E:\\DataScienceProjects\\MCP\\servers\\math\\math.py"],
    }
    
}

async def main():

    # Start MCP multi-server client
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()

    # Map tool names
    named_tools = {tool.name: tool for tool in tools}
    print("Available tools:", list(named_tools.keys()))

    # LLM with tool calling support
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",   # stable, supports tools
        temperature=0
    )

    # Bind tools
    llm_with_tools = llm.bind_tools(tools)

    prompt = "What is 6 * 6 / 7"
    print("\nUser Prompt:", prompt)

    # Start conversation
    messages = [HumanMessage(content=prompt)]

    response = await llm_with_tools.ainvoke(messages)
    
    if not getattr(response, "tool_calls", None):
        response = await llm.ainvoke(messages)
        print("\nFinal Response:", response.content)
        return 
    
    while True:
        # Ask LLM
        response = await llm_with_tools.ainvoke(messages)

        # If no tools → final answer
        if not getattr(response, "tool_calls", None):
            print("\nFinal Response:", response.content)
            break

        # Handle tool calls
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc.get("args") or {}
            tool_call_id = tc["id"]

            print(f"\nTool Requested: {tool_name} | Args: {tool_args}")

            # Run MCP tool
            result = await named_tools[tool_name].ainvoke(tool_args)

            # Send tool result back to LLM
            messages.append(
                ToolMessage(
                    tool_call_id=tool_call_id,
                    content=json.dumps(result)
                )
            )

        # Also append the LLM response itself
        messages.append(response)


if __name__ == "__main__":
    asyncio.run(main())
