from fastmcp import FastMCP, Context
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.utilities.lifespan import combine_lifespans
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from pathlib import Path
import jwt
import uvicorn
import datetime

########################################################################
# Configuration
########################################################################
SECRET_KEY = "my-super-secret-key"
ALGORITHM = "HS256"
ISSUER = "my-fastapi-auth"
AUDIENCE = "my-mcp-server"

########################################################################
# Lifespans
########################################################################
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    print("Starting FastAPI Server...")
    yield
    print("Stopping FastAPI Server...")

@asynccontextmanager
async def mcp_lifespan(app: FastMCP):
    print("Starting MCP Server...")
    db = {
        "employees": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }
    yield {"db": db}
    print("Stopping MCP Server...")

########################################################################
# FastMCP Setup with Auth
########################################################################
verifier = JWTVerifier(
    public_key=SECRET_KEY,
    algorithm=ALGORITHM,
    issuer=ISSUER,
    audience=AUDIENCE
)

mcp = FastMCP(
    name="Company MCP",
    lifespan=mcp_lifespan,
    auth=verifier
)

########################################################################
# Tools, Resources, Prompts
########################################################################
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool
async def list_employees(ctx: Context):
    db = ctx.request_context.lifespan_context["db"]
    return db["employees"]

@mcp.tool
async def greet(name: str, ctx: Context):
    await ctx.info(f"Greeting {name}")
    return f"Hello {name}"

@mcp.resource("company://handbook")
def handbook():
    # Make sure docs/handbook.md exists, or handle gracefully
    try:
        return Path("docs/handbook.md").read_text()
    except Exception:
        return "Handbook not found."

@mcp.resource("employee://{employee_id}")
def employee(employee_id: int):
    return {
        "id": employee_id,
        "department": "Engineering"
    }

@mcp.prompt
def summarize(text: str):
    return f"""
Summarize this text:

{text}
"""

@mcp.prompt
def code_review(language: str):
    return f"""
You are a senior {language} engineer.

Review the following code.
"""

########################################################################
# FastAPI Setup & Routing
########################################################################
mcp_app = mcp.http_app(path="/")
app = FastAPI(lifespan=combine_lifespans(app_lifespan, mcp_app.lifespan))

# Standard FastAPI OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            audience=AUDIENCE,
            issuer=ISSUER
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception: # Catch any JWT error
        raise credentials_exception
    
    return {"username": username}

# Note: OAuth2PasswordRequestForm expects data in form format (application/x-www-form-urlencoded)
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real app, verify against a database
    if form_data.username == "admin" and form_data.password == "admin":
        # Create JWT token
        payload = {
            "sub": form_data.username,
            "iss": ISSUER,
            "aud": AUDIENCE,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=400, detail="Incorrect username or password")

# Example of a standard protected FastAPI route
@app.get("/users/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    uvicorn.run("mcp_server.main:app", host="0.0.0.0", port=8000, reload=True)