# FastMCP Integration Guide

This guide explains how to use the FastMCP client integration in your PocketFlow applications.

## Overview

The FastMCP integration allows you to connect to and use Model Context Protocol (MCP) servers from within your PocketFlow workflows. This enables you to access a wide variety of tools and services, including:

- File system operations
- Web content fetching
- Browser automation
- Sequential thinking tools
- And many more community-developed MCP servers

## Quick Start

### 1. Configuration

Create or modify `config/mcp_servers.json` with your desired MCP servers:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

### 2. Basic Usage

```python
from flows.mcp_example_flow import create_mcp_discovery_flow

# Create and run a discovery flow
shared = {}
flow = create_mcp_discovery_flow()
flow.run(shared)

print(f"Connected servers: {shared['mcp_connected_servers']}")
print(f"Available tools: {len(shared['mcp_tools'])}")
```

### 3. Using MCP Nodes

```python
from nodes.mcp_nodes import MCPInitializeNode, MCPCallToolNode
from pocketflow import Flow

# Initialize MCP service
init_node = MCPInitializeNode()

# Call a specific tool
fetch_node = MCPCallToolNode("fetch", "fetch")

# Create flow
init_node >> fetch_node
flow = Flow(start=init_node)

# Configure and run
shared = {
    "mcp_tool_args_fetch": {"url": "https://httpbin.org/json"}
}
flow.run(shared)

print(shared["mcp_tool_result_fetch"])
```

## Configuration Format

The configuration file uses the following format:

```json
{
  "mcpServers": {
    "server_name": {
      "command": "command_to_run",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      },
      "cwd": "/working/directory"
    }
  }
}
```

### Fields

- **command** (required): The command to execute the MCP server
- **args** (optional): Arguments to pass to the command
- **env** (optional): Environment variables to set
- **cwd** (optional): Working directory for the server

## Available Nodes

### MCPInitializeNode

Initializes the MCP service and connects to all configured servers.

```python
init_node = MCPInitializeNode()
```

**Outputs to shared store:**
- `mcp_init_result`: Initialization results
- `mcp_connected_servers`: List of connected server names

### MCPDiscoverToolsNode

Discovers all available tools from connected servers.

```python
discover_node = MCPDiscoverToolsNode()
```

**Outputs to shared store:**
- `mcp_tools`: List of all available tools
- `mcp_tools_by_server`: Tools grouped by server

### MCPCallToolNode

Calls a specific MCP tool.

```python
tool_node = MCPCallToolNode("tool_name", "server_name")
```

**Reads from shared store:**
- `mcp_tool_args_<tool_name>`: Tool-specific arguments
- `mcp_tool_args`: Generic tool arguments

**Outputs to shared store:**
- `mcp_tool_result_<tool_name>`: Tool-specific result
- `mcp_last_tool_result`: Last tool result

### MCPDynamicToolNode

Calls any tool based on shared store configuration.

```python
dynamic_node = MCPDynamicToolNode()
```

**Reads from shared store:**
- `mcp_dynamic_tool_name`: Tool name to call
- `mcp_dynamic_tool_args`: Arguments for the tool
- `mcp_dynamic_server_name`: Optional server name

**Outputs to shared store:**
- `mcp_dynamic_tool_result`: Tool execution result

### MCPListServersNode

Lists all configured servers and their status.

```python
list_node = MCPListServersNode()
```

**Outputs to shared store:**
- `mcp_servers_info`: Detailed server information

### MCPToolSearchNode

Searches for tools by name or description.

```python
search_node = MCPToolSearchNode()
```

**Reads from shared store:**
- `mcp_search_query`: Search query string

**Outputs to shared store:**
- `mcp_search_results`: Search results

## Example Flows

### Discovery Flow

```python
from flows.mcp_example_flow import create_mcp_discovery_flow

flow = create_mcp_discovery_flow()
shared = {}
flow.run(shared)

# Access results
print(f"Servers: {shared['mcp_connected_servers']}")
print(f"Tools: {len(shared['mcp_tools'])}")
```

### File Operations Flow

```python
from flows.mcp_example_flow import create_mcp_file_operations_flow

shared = {
    "mcp_tool_args_list_directory": {"path": "/tmp"},
    "mcp_tool_args_read_file": {"path": "/tmp/example.txt"}
}

flow = create_mcp_file_operations_flow()
flow.run(shared)

print(shared["mcp_tool_result_list_directory"])
```

### Dynamic Tool Flow

```python
from flows.mcp_example_flow import create_mcp_dynamic_tool_flow

shared = {
    "mcp_dynamic_tool_name": "fetch",
    "mcp_dynamic_tool_args": {"url": "https://httpbin.org/json"},
    "mcp_dynamic_server_name": "fetch"
}

flow = create_mcp_dynamic_tool_flow()
flow.run(shared)

print(shared["mcp_dynamic_tool_result"])
```

## Common MCP Servers

### Filesystem Server

Provides file system operations.

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/root"]
  }
}
```

**Available tools:**
- `list_directory`: List files in a directory
- `read_file`: Read file contents
- `write_file`: Write to a file
- `create_directory`: Create a directory

### Fetch Server

Provides web content fetching.

```json
{
  "fetch": {
    "command": "uvx",
    "args": ["mcp-server-fetch"]
  }
}
```

**Available tools:**
- `fetch`: Fetch content from a URL

### Browser MCP

Provides browser automation capabilities.

```json
{
  "browsermcp": {
    "command": "npx",
    "args": ["@browsermcp/mcp@latest"]
  }
}
```

## Error Handling

The MCP integration includes comprehensive error handling:

1. **Configuration errors**: Invalid JSON or missing servers
2. **Connection errors**: Server startup failures
3. **Tool execution errors**: Runtime errors during tool calls

Check the `error_message` field in server info for troubleshooting:

```python
servers = service.get_server_info()
for server in servers:
    if server.status == "error":
        print(f"Server {server.name} error: {server.error_message}")
```

## Testing

Run the test suite to verify your MCP integration:

```bash
# Run all tests
docker-compose run test

# Run specific test file
docker-compose run test pytest tests/test_mcp_config.py -v
```

## Docker Compose Usage

The project includes a docker-compose setup for easy testing:

```bash
# Build and run the application
docker-compose up app

# Run tests
docker-compose run test

# Run with MCP servers
docker-compose up
```

## Troubleshooting

### Server Connection Issues

1. **Check server installation**: Ensure MCP servers are installed
   ```bash
   npx @modelcontextprotocol/server-filesystem --version
   uvx mcp-server-fetch --help
   ```

2. **Verify commands**: Make sure `npx` and `uvx` are available
   ```bash
   which npx
   which uvx
   ```

3. **Check logs**: Enable debug logging
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Tool Execution Issues

1. **Verify tool exists**: Use discovery flow to list available tools
2. **Check arguments**: Ensure tool arguments match the expected schema
3. **Server status**: Verify the server is connected before calling tools

### Configuration Issues

1. **Validate JSON**: Use a JSON validator to check syntax
2. **Check paths**: Ensure file paths and working directories exist
3. **Environment variables**: Verify required environment variables are set

## Advanced Usage

### Custom Nodes

Create custom nodes that extend the MCP functionality:

```python
from nodes.mcp_nodes import MCPServiceNode

class CustomMCPNode(MCPServiceNode):
    def exec(self, prep_data):
        service = self.get_mcp_service()
        # Your custom logic here
        return result
```

### Async Operations

For advanced use cases, you can work directly with the async MCP service:

```python
import asyncio
from utils.mcp_service import MCPService

async def advanced_mcp_usage():
    service = MCPService()
    async with service:
        tools = service.get_all_tools()
        result = await service.call_tool("fetch", {"url": "https://example.com"})
        return result

result = asyncio.run(advanced_mcp_usage())
```

## Contributing

To add new MCP servers or improve the integration:

1. Add server configuration to `config/mcp_servers.json`
2. Create example flows in `flows/`
3. Add tests in `tests/`
4. Update documentation

## Resources

- [FastMCP Documentation](https://gofastmcp.com/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [PocketFlow Documentation](https://the-pocket.github.io/PocketFlow/)
