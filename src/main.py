import asyncio
import httpx
import os
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

async def get_token():
    """Obtain JWT token from the FastAPI server."""
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            "http://127.0.0.1:8000/login",
            data={"username": "admin", "password": "admin"}
        )
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.text}")
        return response.json()["access_token"]


async def main():
    print("🔐 Authenticating with server...")
    token = await get_token()
    print("✅ Authenticated successfully\n")

    # Connect to MCP server with MultiServerMCPClient using custom auth header
    print("🚀 Configuring MCP Client...")
    mcp_client = MultiServerMCPClient(
        {
            "company_mcp": {
                "transport": "http",
                # Thêm dấu / ở cuối để tránh FastAPI 307 Redirect
                "url": "http://127.0.0.1:8000/mcp/", 
                "headers": {
                    "Authorization": f"Bearer {token}"
                }
            }
        }
    )

    # Dùng Stateful Session để giữ 1 kết nối duy nhất, không tạo mới session liên tục
    print("🔄 Loading tools from MCP Server...")
    async with mcp_client.session("company_mcp") as session:
        mcp_tools = await load_mcp_tools(session)
        print(f"✅ Loaded {len(mcp_tools)} tools: {[t.name for t in mcp_tools]}\n")

        # Phân loại tools cho từng subagent
        # Các tools từ MultiServerMCPClient sẽ có prefix server_name: "company_mcp_add", "company_mcp_list_employees", v.v.
        # Nên ta dùng kiểm tra chuỗi để chia tool
        hr_tools = [t for t in mcp_tools if "list_employees" in t.name or "greet" in t.name]
        math_tools = [t for t in mcp_tools if "add" in t.name]

        # ---------------------------------------------------------
        # Define Subagents Configs
        # ---------------------------------------------------------
        
        hr_subagent = {
            "name": "hr-assistant",
            "description": "Use this subagent to interact with human resources data, such as listing employees and greeting them.",
            "system_prompt": "You are an HR assistant. Use your tools to interact with employee data. Return clear and concise answers.",
            "tools": hr_tools,
        }

        math_subagent = {
            "name": "math-assistant",
            "description": "Use this subagent to perform mathematical calculations like adding numbers.",
            "system_prompt": "You are a precise calculator. Use your tool to add numbers exactly.",
            "tools": math_tools,
        }

        # ---------------------------------------------------------
        # Create Main Deep Agent
        # ---------------------------------------------------------
        
        print("🤖 Creating Deep Agent with MCP tools and Subagents...")
        
        agent = create_deep_agent(
            model="openai:gemini-3-flash", # Uses LiteLLM (via OPENAI_BASE_URL)
            system_prompt=(
                "You are a high-level project coordinator. You MUST delegate tasks to your subagents.\n"
                "Use the 'task' tool to delegate math calculations to 'math-assistant' and employee data queries to 'hr-assistant'.\n"
                "Never perform calculations or employee lookups yourself."
            ),
            subagents=[hr_subagent, math_subagent],
        )

        # ---------------------------------------------------------
        # Invoke Agent with Streaming
        # ---------------------------------------------------------
        
        query = "Can you add 150 and 320 for me? Also, list all the employees in the database and then greet 'Alice'."
        print(f"\n👤 User Request: {query}\n")
        print("⏳ Agent is processing... (Live Stream)\n")

        # Sử dụng astream_events để in ra từng bước suy nghĩ của Agent và Subagent
        stream = agent.astream_events(
            {"messages": [{"role": "user", "content": query}]},
            version="v2",
        )

        try:
            async for event in stream:
                kind = event["event"]
                name = event.get("name")
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and isinstance(chunk.content, str):
                        print(chunk.content, end="", flush=True)
                elif kind == "on_tool_start":
                    print(f"\n[⚙️ Calling Tool: {name} with args: {event['data'].get('input')}]")
                elif kind == "on_tool_end":
                    print(f"[✅ Tool {name} Finished]")
        except KeyboardInterrupt:
            print("\n\n❌ Aborted by user.")
        
        print("\n\n🎯 Workflow Complete!")


if __name__ == "__main__":
    asyncio.run(main())
