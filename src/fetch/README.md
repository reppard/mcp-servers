# Fetch MCP Server

A Model Context Protocol server that provides web content fetching capabilities. This server enables LLMs to retrieve and process content from web pages, converting HTML to markdown for easier consumption.

The fetch tool will truncate the response, but by using the `start_index` argument, you can specify where to start the content extraction. This lets models read a webpage in chunks, until they find the information they need.

### Available Tools

- `fetch` - Fetches a URL from the internet and extracts its contents as markdown.
    - `url` (string, required): URL to fetch
    - `max_length` (integer, optional): Maximum number of characters to return (default: 5000)
    - `start_index` (integer, optional): Start content from this character index (default: 0)
    - `raw` (boolean, optional): Get raw content without markdown conversion (default: false)

### Prompts

- **fetch**
  - Fetch a URL and extract its contents as markdown
  - Arguments:
    - `url` (string, required): URL to fetch

## Installation

Optionally: Install node.js, this will cause the fetch server to use a different HTML simplifier that is more robust.

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-fetch*.

### Using PIP

Alternatively you can install `mcp-server-fetch` via pip:

```
pip install mcp-server-fetch
```

After installation, you can run it as a script using:

```
python -m mcp_server_fetch
```

## Server Modes

The fetch server can run in two modes:

### 1. Standard Mode (Default)

The standard mode uses stdio for communication and is suitable for local development and CLI usage:

```
python -m mcp_server_fetch
```

### 2. SSE Mode

The SSE (Server-Sent Events) mode runs a web server on port 3001 and provides both HTTP and SSE endpoints:

```
python -m mcp_server_fetch.sse_server
```

The SSE server provides two endpoints:
- `GET /events` - SSE endpoint for real-time updates
- `POST /messages` - Endpoint for MCP protocol messages

You can also run it using uvicorn directly:

```
uvicorn mcp_server_fetch.sse_server:app --host 0.0.0.0 --port 3001
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx (Standard Mode)</summary>

```json
"mcpServers": {
  "fetch": {
    "command": "uvx",
    "args": ["mcp-server-fetch"]
  }
}
```
</details>

<details>
<summary>Using docker (Standard Mode)</summary>

```json
"mcpServers": {
  "fetch": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "mcp/fetch"]
  }
}
```
</details>

<details>
<summary>Using docker (SSE Mode)</summary>

```json
"mcpServers": {
  "fetch": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "-p", "3001:3001", "mcp/fetch", "sse"]
  }
}
```
</details>

<details>
<summary>Using pip installation (Standard Mode)</summary>

```json
"mcpServers": {
  "fetch": {
    "command": "python",
    "args": ["-m", "mcp_server_fetch"]
  }
}
```
</details>

<details>
<summary>Using pip installation (SSE Mode)</summary>

```json
"mcpServers": {
  "fetch": {
    "command": "python",
    "args": ["-m", "mcp_server_fetch.sse_server"]
  }
}
```
</details>

### Customization - robots.txt

By default, the server will obey a websites robots.txt file if the request came from the model (via a tool), but not if
the request was user initiated (via a prompt). This can be disabled by adding the argument `--ignore-robots-txt` to the
`args` list in the configuration.

### Customization - User-agent

By default, depending on if the request came from the model (via a tool), or was user initiated (via a prompt), the
server will use either the user-agent
```
ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)
```
or
```
ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)
```

This can be customized by adding the argument `--user-agent=YourUserAgent` to the `args` list in the configuration.

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```
npx @modelcontextprotocol/inspector uvx mcp-server-fetch
```

Or if you've installed the package in a specific directory or are developing on it:

```
cd path/to/servers/src/fetch
npx @modelcontextprotocol/inspector uv run mcp-server-fetch
```

For the SSE server, you can use standard HTTP debugging tools or the MCP inspector with the appropriate configuration.

## Contributing

We encourage contributions to help expand and improve mcp-server-fetch. Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see:
https://github.com/modelcontextprotocol/servers

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements to make mcp-server-fetch even more powerful and useful.

## License

mcp-server-fetch is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.

## Running with Docker Compose

The fetch server can be run using Docker Compose in either stdio or SSE mode.

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. Clone the repository and navigate to the fetch server directory:
```bash
cd src/fetch
```

2. Start the server in SSE mode (recommended for most use cases):
```bash
docker-compose up fetch-sse
```

Or start in stdio mode:
```bash
docker-compose up fetch-stdio
```

### Configuration

The docker-compose.yml file provides two services:

- `fetch-sse`: Runs the server in SSE mode, exposing port 3001
- `fetch-stdio`: Runs the server in stdio mode for direct integration

Both services:
- Use the same Docker image
- Mount a `data` directory for persistence
- Have Python output unbuffered for better logging

### Environment Variables

You can add environment variables to the docker-compose.yml file under the `environment` section of each service.

### Health Checks

The SSE mode includes a health check that pings the /health endpoint every 30 seconds.

### Data Persistence

Both services mount a `data` directory from the host to `/app/data` in the container. Create this directory before starting the services:

```bash
mkdir -p data
```
