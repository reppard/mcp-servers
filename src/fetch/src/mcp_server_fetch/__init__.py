from .server import serve
from .sse_server import app

__version__ = "0.6.2"

async def main() -> None:
    """Run the fetch MCP server."""
    await serve()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
