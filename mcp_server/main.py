from fastmcp import FastMCP, Context
from contextlib import asynccontextmanager
from pathlib import Path

########################################################################
# Lifespan
########################################################################

@asynccontextmanager
async def lifespan(app: FastMCP):

    print("Starting MCP Server...")

    db = {
        "employees": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }

    yield {
        "db": db
    }

    print("Stopping MCP Server...")


########################################################################
# Create Server
########################################################################

mcp = FastMCP(
    name="Company MCP",
    lifespan=lifespan
)

########################################################################
# Tool
########################################################################

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""

    return a + b


########################################################################
# Tool using Context
########################################################################

@mcp.tool
async def list_employees(ctx: Context):

    db = ctx.request_context.lifespan_context["db"]

    return db["employees"]


########################################################################
# Tool with logging
########################################################################

@mcp.tool
async def greet(name: str, ctx: Context):

    await ctx.info(f"Greeting {name}")

    return f"Hello {name}"


########################################################################
# Resource
########################################################################

@mcp.resource("company://handbook")
def handbook():

    return Path("docs/handbook.md").read_text()


########################################################################
# Dynamic Resource
########################################################################

@mcp.resource("employee://{employee_id}")
def employee(employee_id: int):

    return {
        "id": employee_id,
        "department": "Engineering"
    }


########################################################################
# Prompt
########################################################################

@mcp.prompt
def summarize(text: str):

    return f"""
Summarize this text:

{text}
"""


########################################################################
# Prompt with arguments
########################################################################

@mcp.prompt
def code_review(language: str):

    return f"""
You are a senior {language} engineer.

Review the following code.
"""


########################################################################

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
    )