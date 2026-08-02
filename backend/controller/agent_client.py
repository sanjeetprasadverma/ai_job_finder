import os
from contextlib import AsyncExitStack

from ollama import AsyncClient
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:latest")

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://job-mcp:8000/mcp")

ollama_client = AsyncClient( host="http://ollama:11434")

SYSTEM_PROMPT = (
    "You help users find job postings. When the user describes what they're "
    "looking for, use the search_jobs tool to find matches, then summarize the "
    "results conversationally — mention the job title, company, and why it "
    "matches. If no jobs are found, say so plainly and suggest broadening the search."
)


def _mcp_tool_to_ollama_schema(tool):
    """Convert an MCP tool definition into the shape Ollama's chat() expects."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


async def run_agent(user_text: str) -> str:
    """
    Run one full turn: user_text -> Ollama (with MCP tools available) -> final reply text.

    Opens a fresh HTTP connection to the external MCP server per call, which is
    fine for typical Telegram bot traffic. If you need lower latency under heavy
    load, keep a long-lived ClientSession instead of reconnecting every message.
    """
    print("1. Starting agent")
    async with AsyncExitStack() as stack:
        print("2. Connecting MCP")
        read, write = await stack.enter_async_context(
            streamable_http_client(MCP_SERVER_URL)
        )
        print("3. MCP transport connected")
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        print("4. MCP initialized")
        
        tools_result = await session.list_tools()
        print("5. Received tools")
        print(tools_result.tools)
        tools = [_mcp_tool_to_ollama_schema(t) for t in tools_result.tools]

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ]
        print("6. Sending request to Ollama")
        response = await ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            tools=tools,
        )
        print("8. Ollama responded")
        print(response.message)
        messages.append(response.message)

        # Keep looping while the model wants to call tools
        while response.message.tool_calls:
            for call in response.message.tool_calls:
                result = await session.call_tool(call.function.name, call.function.arguments)
                result_text = "".join(
                    part.text for part in result.content if hasattr(part, "text")
                )
                messages.append({
                    "role": "tool",
                    "tool_name": call.function.name,
                    "content": result_text,
                })

            response = await ollama_client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=tools,
            )
            messages.append(response.message)

        return response.message.content or "Sorry, I couldn't find anything for that."