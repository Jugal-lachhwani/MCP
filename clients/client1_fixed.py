import asyncio
import sys
import json
import traceback
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage

load_dotenv()

PYTHON = sys.executable

SERVERS = {
    "math": {
        "transport": "stdio",
        "command": PYTHON,
        # Use unbuffered mode so stdio communication is immediate
        "args": ["-u", r"E:\\DataScienceProjects\\MCP\\servers\\math\\math.py"],
    }
}


async def main():
    try:
        client = MultiServerMCPClient(SERVERS)
        tools = await client.get_tools()

        tool_names = {t.name: t for t in tools}

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        llm_with_tools = llm.bind_tools(tools)

        prompt = "What is the capital of India"

        # iterate so we can handle chains of multiple tool calls
        messages = [HumanMessage(content=prompt)]

        while True:
            res = await llm_with_tools.ainvoke(messages)

            # debug: show raw response fields
            print('RAW RES:', getattr(res, '__dict__', repr(res)))

            if not getattr(res, 'tool_calls', None):
                print('Final answer:', getattr(res, 'content', None))
                break

            for call in res.tool_calls:
                selected_tool = call.get('name')
                selected_tool_args = call.get('args', {}) or {}
                selected_tool_id = call.get('id')

                print('The selected tool is', selected_tool)
                print('Selected_tool args is', selected_tool_args)

                tool = tool_names[selected_tool]
                tool_result = None
                try:
                    if hasattr(tool, 'ainvoke'):
                        tool_result = await tool.ainvoke(selected_tool_args)
                    elif hasattr(tool, 'arun'):
                        if isinstance(selected_tool_args, dict):
                            tool_result = await tool.arun(**selected_tool_args)
                        else:
                            tool_result = await tool.arun(selected_tool_args)
                    elif hasattr(tool, 'coroutine'):
                        tool_result = await tool.coroutine(selected_tool_args)
                    elif hasattr(tool, 'run'):
                        if isinstance(selected_tool_args, dict):
                            tool_result = tool.run(**selected_tool_args)
                        else:
                            tool_result = tool.run(selected_tool_args)
                except Exception:
                    traceback.print_exc()

                tool_result_str = json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result
                print('And the result is', tool_result_str)

                # append the model's latest reply (as AIMessage) then the tool output
                messages.append(AIMessage(content=getattr(res, 'content', '') or ''))
                messages.append(ToolMessage(content=tool_result_str, tool_call_id=selected_tool_id))
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
