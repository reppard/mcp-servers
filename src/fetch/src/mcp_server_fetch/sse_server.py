from typing import Annotated, Tuple
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from mcp.server import Server
from mcp.types import TextContent
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request
from .server import (
    Fetch,
    fetch_url,
    check_may_autonomously_fetch_url,
    DEFAULT_USER_AGENT_AUTONOMOUS,
    DEFAULT_USER_AGENT_MANUAL,
)

# Create MCP server instance
mcp_server = Server("mcp-fetch-sse")
user_agent_autonomous = DEFAULT_USER_AGENT_AUTONOMOUS
user_agent_manual = DEFAULT_USER_AGENT_MANUAL

# Create SSE transport
sse = SseServerTransport("/messages")

async def handle_sse(request: Request):
    """Handle SSE connection requests."""
    async def event_generator():
        # Create a dummy receive/send pair for the SSE connection
        async def receive():
            return {"type": "http.disconnect"}
            
        async def send(message):
            if message["type"] == "http.response.start":
                yield {"event": "connected", "data": json.dumps({"type": "connected"})}
            elif message["type"] == "http.response.body":
                if message.get("body"):
                    yield {"event": "message", "data": message["body"].decode()}
            elif message["type"] == "http.disconnect":
                return
                
        # Connect to the SSE transport
        async with sse.connect_sse(request.scope, receive, send) as streams:
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
            
    return EventSourceResponse(event_generator())

async def handle_messages(request: Request):
    """Handle POST messages for the SSE transport."""
    # Extract the message from the request body
    message = await request.json()
    # Create a dummy receive/send pair for the message
    async def receive():
        return {"type": "http.request", "body": json.dumps(message).encode()}
    async def send(message):
        pass  # We don't need to do anything with the response here
    # Handle the message
    await sse.handle_post_message(request.scope, receive, send)
    return JSONResponse({"status": "ok"})

# Create Starlette app with SSE routes
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001) 