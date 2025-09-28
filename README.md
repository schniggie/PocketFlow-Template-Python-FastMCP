<h1 align="center">PocketFlow Template with FastMCP Integration</h1>

<p align="center">
  <a href="https://github.com/The-Pocket/PocketFlow" target="_blank">
    <img 
      src="./assets/banner.png" width="800"
    />
  </a>
</p>

This is a project template for Agentic Coding with [PocketFlow](https://github.com/The-Pocket/PocketFlow), a 100-line LLM framework, enhanced with [FastMCP](https://gofastmcp.com/) client integration for accessing Model Context Protocol (MCP) servers.

## 🚀 Features

- **PocketFlow Integration**: Build LLM workflows with the minimalist PocketFlow framework
- **FastMCP Client**: Connect to and use MCP servers for extended functionality
- **Docker Support**: Complete containerized development environment
- **Test-Driven Development**: Comprehensive test suite with pytest
- **Multiple MCP Servers**: Pre-configured support for filesystem, fetch, browser, and more
- **AI Assistant Rules**: Configuration files for various AI coding assistants

## 🏗️ Architecture

The template provides:

- **MCP Configuration Management**: JSON-based server configuration with validation
- **MCP Service Layer**: Async service for managing MCP client connections
- **PocketFlow Nodes**: Ready-to-use nodes for MCP operations
- **Example Flows**: Demonstration flows for common MCP use cases
- **Comprehensive Testing**: Unit and integration tests

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- Node.js and npm (for MCP servers)
- uv (for Python package management)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd PocketFlow-Template-Python-FastMCP
```

### 2. Automated Setup (Recommended)

```bash
# Run the setup script to install dependencies and test everything
python setup.py
```

This will:
- Check Python version compatibility (3.11+ required)
- Check system dependencies (Node.js, npm, Docker)
- Install all Python dependencies
- Run tests to verify installation

### 3. Manual Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Test the installation
python test_basic.py

# Run the application
python main.py
```

### 4. Docker Development (Alternative)

```bash
# Build and run the application
docker-compose up app

# Run tests
docker-compose run test
```

## 🔧 Configuration

### MCP Servers Configuration

Edit `config/mcp_servers.json` to configure your MCP servers:

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

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for LLM calls
- `RUN_MCP_DEMO`: Set to "false" to skip MCP demonstration (default: "true")

## 🔧 Troubleshooting

### Common Issues

#### "No module named 'fastmcp'" Error

This means the FastMCP dependency is not installed. Fix with:

```bash
# Option 1: Run the setup script
python setup.py

# Option 2: Install manually
pip install -r requirements.txt

# Option 3: Install specific package
pip install fastmcp>=2.12.0
```

#### "No module named 'pocketflow'" Error

Install the PocketFlow framework:

```bash
pip install pocketflow>=0.0.1
```

#### MCP Server Connection Issues

1. Ensure Node.js and npm are installed
2. Check that MCP server commands are available:
   ```bash
   npx @modelcontextprotocol/server-filesystem --version
   uvx mcp-server-fetch --version
   ```
3. Verify your `config/mcp_servers.json` configuration

#### Python Version Issues

This template requires Python 3.11+. Check your version:

```bash
python --version
```

If you have an older version, consider using pyenv or conda to install Python 3.11+.

## 📚 Usage Examples

### Basic MCP Discovery

```python
from flows.mcp_example_flow import run_discovery_flow

# Discover available MCP servers and tools
result = run_discovery_flow()
print(f"Connected servers: {result['mcp_connected_servers']}")
```

### File Operations

```python
from flows.mcp_example_flow import create_mcp_file_operations_flow

shared = {
    "mcp_tool_args_list_directory": {"path": "/tmp"}
}

flow = create_mcp_file_operations_flow()
flow.run(shared)
```

### Dynamic Tool Calling

```python
from nodes.mcp_nodes import MCPDynamicToolNode

# Configure dynamic tool call
shared = {
    "mcp_dynamic_tool_name": "fetch",
    "mcp_dynamic_tool_args": {"url": "https://httpbin.org/json"}
}

node = MCPDynamicToolNode()
result = node.exec(shared)
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Run all tests
docker-compose run test

# Run specific test categories
pytest tests/test_mcp_config.py -v
pytest tests/test_mcp_service.py -v
pytest tests/test_mcp_nodes.py -v

# Run with coverage
pytest tests/ --cov=utils --cov=nodes --cov=flows
```

## 📖 Documentation

- [FastMCP Integration Guide](docs/mcp_integration.md) - Comprehensive guide to using MCP features
- [PocketFlow Documentation](https://the-pocket.github.io/PocketFlow/) - Core framework documentation
- [FastMCP Documentation](https://gofastmcp.com/) - FastMCP client documentation

## 🛠️ Available MCP Servers

The template includes configuration for popular MCP servers:

- **Filesystem**: File system operations (list, read, write files)
- **Fetch**: Web content fetching and HTTP requests
- **Browser MCP**: Browser automation capabilities
- **Sequential Thinking Tools**: Advanced reasoning tools

## 🏗️ Project Structure

```
├── config/
│   └── mcp_servers.json          # MCP server configuration
├── docs/
│   └── mcp_integration.md        # Integration documentation
├── flows/
│   └── mcp_example_flow.py       # Example MCP flows
├── nodes/
│   └── mcp_nodes.py              # MCP-enabled PocketFlow nodes
├── tests/
│   ├── test_mcp_config.py        # Configuration tests
│   ├── test_mcp_service.py       # Service layer tests
│   └── test_mcp_nodes.py         # Node tests
├── utils/
│   ├── mcp_config.py             # Configuration management
│   ├── mcp_service.py            # MCP service layer
│   └── call_llm.py               # LLM utility
├── docker-compose.yml            # Docker services
├── Dockerfile                    # Application container
├── main.py                       # Main application
└── requirements.txt              # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 🔗 AI Assistant Configuration

We have included rules files for various AI coding assistants:
- [.cursorrules](.cursorrules) for Cursor AI
- [.clinerules](.clinerules) for Cline
- [.windsurfrules](.windsurfrules) for Windsurf
- [.goosehints](.goosehints) for Goose
- Configuration in [.github](.github) for GitHub Copilot
- [CLAUDE.md](CLAUDE.md) for Claude Code
- [GEMINI.md](GEMINI.md) for Gemini

## 📚 Learning Resources

- [Agentic Coding Guidance](https://the-pocket.github.io/PocketFlow/guide.html)
- [YouTube Tutorial](https://www.youtube.com/@ZacharyLLM?sub_confirmation=1)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
