import asyncio
from fastmcp import Client


async def main():
    # Initialize the FastMCP client to point to the server's HTTP streamable endpoint
    client = Client("http://0.0.0.0:8000/mcp")

    print("\n🚀 Connecting to FastMCP Server...")
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
        handbook = await client.read_resource("company://handbook")
        
        # Ensure we only print a preview if it's too long
        handbook_text = handbook[0].text
        preview = handbook_text[:50].replace('\n', ' ') + "..." if len(handbook_text) > 50 else handbook_text
        print(f"   [company://handbook] -> {preview}")

        employee = await client.read_resource("employee://1")
        print(f"   [employee://1] -> {employee[0].text}\n")

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
