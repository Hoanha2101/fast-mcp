import asyncio
import httpx
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp import Client


async def get_token():
    """
    Login to the FastAPI server and obtain a JWT token.
    """
    print("\n🔐 Authenticating with FastAPI Server...")
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            "http://127.0.0.1:8000/login",
            data={"username": "admin", "password": "admin"}
        )
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return None
        token = response.json()["access_token"]
        print("✅ Authenticated successfully!\n")
        return token


async def main():
    # 1. Obtain Token
    token = await get_token()
    if not token:
        return

    # 2. Setup Transport with Auth Header
    transport = StreamableHttpTransport(
        url="http://127.0.0.1:8000/mcp",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 3. Initialize the FastMCP client with the authenticated transport
    client = Client(transport)

    print("🚀 Connecting to FastMCP Server...")
    async with client:
        print("✅ Connected!\n")

        # ---------------------------------------------------------
        # 1. List Available Tools
        # ---------------------------------------------------------
        print("🛠️  === Available Tools ===")
        tools = await client.list_tools()
        for i, tool in enumerate(tools, 1):
            desc = tool.description or "No description"
            print(f"   {i}. {tool.name} - {desc}")
        print()

        # ---------------------------------------------------------
        # 2. Call Tools
        # ---------------------------------------------------------
        print("⚡ === Executing Tools ===")
        add_result = await client.call_tool("add", {"a": 10, "b": 20})
        print(f"   [add(10, 20)] -> Result: {add_result.data}")

        employees_result = await client.call_tool("list_employees")
        print(f"   [list_employees] -> Result: {employees_result.content[0].text}\n")

        # ---------------------------------------------------------
        # 3. Read Resources
        # ---------------------------------------------------------
        print("📄 === Reading Resources ===")
        try:
            handbook = await client.read_resource("company://handbook")
            handbook_text = handbook[0].text
            preview = handbook_text[:50].replace('\n', ' ') + "..." if len(handbook_text) > 50 else handbook_text
            print(f"   [company://handbook] -> {preview}")
        except Exception as e:
            print(f"   [company://handbook] -> Error: {e}")

        try:
            employee = await client.read_resource("employee://1")
            print(f"   [employee://1] -> {employee[0].text}\n")
        except Exception as e:
            print(f"   [employee://1] -> Error: {e}\n")

        # ---------------------------------------------------------
        # 4. Use Prompts
        # ---------------------------------------------------------
        print("🤖 === Generating Prompts ===")
        prompt_summarize = await client.get_prompt("summarize", {"text": "FastMCP is awesome."})
        print(f"   [summarize] -> '{prompt_summarize.messages[0].content.text.strip()}'")

        prompt_review = await client.get_prompt("code_review", {"language": "Python"})
        print(f"   [code_review] -> '{prompt_review.messages[0].content.text.strip()}'\n")

    print("🏁 Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
