# FastMCP Example Project 🚀

This repository contains a simple client-server setup demonstrating the power of the **Model Context Protocol (MCP)** using the `fastmcp` Python library.

## 📁 Structure
- `mcp_server/`: Contains the FastMCP server setup (`main.py`) which exposes tools, resources, and prompts. Also contains a `docs/` folder for reading local files.
- `client/`: Contains the MCP Client (`main.py`) which connects to the server and invokes these endpoints over HTTP.

## 🚀 Features Demonstrated
1. **Tools (`@mcp.tool`)**: 
   - Exposing functions that AI agents or clients can invoke (e.g., `add`, `list_employees`, `greet`).
2. **Resources (`@mcp.resource`)**:
   - Reading static resources like a company handbook.
   - Reading dynamic resources using parameters (e.g., `employee://{employee_id}`).
3. **Prompts (`@mcp.prompt`)**:
   - Serving predefined, parameterized prompts ready for LLM consumption (e.g., `summarize`, `code_review`).

## 🛠️ How to Run

### 1. Start the Server
Navigate to the server directory and run the server script:
```bash
cd mcp_server
python main.py
```
*The server will start listening on `http://0.0.0.0:8000/mcp` using the streamable-http transport.*

### 2. Run the Client
Open a new terminal window, navigate to the client directory, and run the client script:
```bash
cd client
python main.py
```
*The client will connect, list all available endpoints, and print beautifully formatted results for tools, resources, and prompts.*

## 📝 Prerequisites
- Python 3.10+
- `fastmcp` (install via `pip install fastmcp`)

Enjoy building context-aware AI tools!
