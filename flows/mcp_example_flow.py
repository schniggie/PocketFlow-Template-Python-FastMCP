"""
MCP Example Flows

This module demonstrates how to create PocketFlow flows that use MCP servers
for various tasks like file operations, web fetching, and tool discovery.
"""

from pocketflow import Flow
from nodes.mcp_nodes import (
    MCPInitializeNode,
    MCPDiscoverToolsNode,
    MCPListServersNode,
    MCPCallToolNode,
    MCPDynamicToolNode,
    MCPToolSearchNode
)


def create_mcp_discovery_flow():
    """
    Create a flow that initializes MCP service and discovers available tools.
    
    This flow:
    1. Initializes the MCP service and connects to servers
    2. Discovers all available tools
    3. Lists server status information
    """
    # Create nodes
    init_node = MCPInitializeNode()
    discover_node = MCPDiscoverToolsNode()
    list_servers_node = MCPListServersNode()
    
    # Connect nodes in sequence
    init_node >> discover_node >> list_servers_node
    
    # Create and return flow
    return Flow(start=init_node)


def create_mcp_file_operations_flow():
    """
    Create a flow that demonstrates file operations using MCP filesystem server.
    
    This flow:
    1. Initializes MCP service
    2. Lists files in a directory
    3. Reads a specific file
    """
    # Create nodes
    init_node = MCPInitializeNode()
    
    # Node to list files (assumes filesystem server is configured)
    list_files_node = MCPCallToolNode("list_directory", "filesystem")
    
    # Node to read a file
    read_file_node = MCPCallToolNode("read_file", "filesystem")
    
    # Connect nodes
    init_node >> list_files_node >> read_file_node
    
    return Flow(start=init_node)


def create_mcp_web_fetch_flow():
    """
    Create a flow that demonstrates web fetching using MCP fetch server.
    
    This flow:
    1. Initializes MCP service
    2. Fetches content from a URL
    """
    # Create nodes
    init_node = MCPInitializeNode()
    
    # Node to fetch web content
    fetch_node = MCPCallToolNode("fetch", "fetch")
    
    # Connect nodes
    init_node >> fetch_node
    
    return Flow(start=init_node)


def create_mcp_dynamic_tool_flow():
    """
    Create a flow that uses dynamic tool calling based on shared store configuration.
    
    This flow:
    1. Initializes MCP service
    2. Discovers available tools
    3. Calls a tool dynamically based on shared store settings
    """
    # Create nodes
    init_node = MCPInitializeNode()
    discover_node = MCPDiscoverToolsNode()
    dynamic_tool_node = MCPDynamicToolNode()
    
    # Connect nodes
    init_node >> discover_node >> dynamic_tool_node
    
    return Flow(start=init_node)


def create_mcp_tool_search_flow():
    """
    Create a flow that searches for tools and then calls one of them.
    
    This flow:
    1. Initializes MCP service
    2. Searches for tools matching a query
    3. Calls a dynamic tool based on search results
    """
    # Create nodes
    init_node = MCPInitializeNode()
    search_node = MCPToolSearchNode()
    dynamic_tool_node = MCPDynamicToolNode()
    
    # Connect nodes
    init_node >> search_node >> dynamic_tool_node
    
    return Flow(start=init_node)


def create_mcp_comprehensive_flow():
    """
    Create a comprehensive flow that demonstrates multiple MCP capabilities.
    
    This flow:
    1. Initializes MCP service
    2. Lists all servers and their status
    3. Discovers all available tools
    4. Searches for specific tools
    5. Calls a dynamic tool
    """
    # Create nodes
    init_node = MCPInitializeNode()
    list_servers_node = MCPListServersNode()
    discover_node = MCPDiscoverToolsNode()
    search_node = MCPToolSearchNode()
    dynamic_tool_node = MCPDynamicToolNode()
    
    # Connect nodes in sequence
    init_node >> list_servers_node >> discover_node >> search_node >> dynamic_tool_node
    
    return Flow(start=init_node)


# Example usage functions for each flow
def run_discovery_flow():
    """Run the MCP discovery flow example."""
    shared = {}
    
    flow = create_mcp_discovery_flow()
    flow.run(shared)
    
    print("=== MCP Discovery Flow Results ===")
    print(f"Initialization: {shared.get('mcp_init_result', {})}")
    print(f"Connected servers: {shared.get('mcp_connected_servers', [])}")
    print(f"Total tools discovered: {len(shared.get('mcp_tools', []))}")
    print(f"Server info: {shared.get('mcp_servers_info', {})}")
    
    return shared


def run_file_operations_flow():
    """Run the MCP file operations flow example."""
    shared = {
        # Configure file operations
        "mcp_tool_args_list_directory": {"path": "/tmp"},
        "mcp_tool_args_read_file": {"path": "/tmp/example.txt"}
    }
    
    flow = create_mcp_file_operations_flow()
    flow.run(shared)
    
    print("=== MCP File Operations Flow Results ===")
    print(f"List directory result: {shared.get('mcp_tool_result_list_directory', {})}")
    print(f"Read file result: {shared.get('mcp_tool_result_read_file', {})}")
    
    return shared


def run_web_fetch_flow():
    """Run the MCP web fetch flow example."""
    shared = {
        # Configure web fetch
        "mcp_tool_args_fetch": {"url": "https://httpbin.org/json"}
    }
    
    flow = create_mcp_web_fetch_flow()
    flow.run(shared)
    
    print("=== MCP Web Fetch Flow Results ===")
    print(f"Fetch result: {shared.get('mcp_tool_result_fetch', {})}")
    
    return shared


def run_dynamic_tool_flow():
    """Run the MCP dynamic tool flow example."""
    shared = {
        # Configure dynamic tool call
        "mcp_dynamic_tool_name": "list_directory",
        "mcp_dynamic_tool_args": {"path": "/tmp"},
        "mcp_dynamic_server_name": "filesystem"
    }
    
    flow = create_mcp_dynamic_tool_flow()
    flow.run(shared)
    
    print("=== MCP Dynamic Tool Flow Results ===")
    print(f"Dynamic tool result: {shared.get('mcp_dynamic_tool_result', {})}")
    
    return shared


def run_tool_search_flow():
    """Run the MCP tool search flow example."""
    shared = {
        # Configure tool search
        "mcp_search_query": "list",
        # After search, configure dynamic tool call
        "mcp_dynamic_tool_name": "list_directory",
        "mcp_dynamic_tool_args": {"path": "/tmp"},
        "mcp_dynamic_server_name": "filesystem"
    }
    
    flow = create_mcp_tool_search_flow()
    flow.run(shared)
    
    print("=== MCP Tool Search Flow Results ===")
    print(f"Search results: {shared.get('mcp_search_results', {})}")
    print(f"Dynamic tool result: {shared.get('mcp_dynamic_tool_result', {})}")
    
    return shared


def run_comprehensive_flow():
    """Run the comprehensive MCP flow example."""
    shared = {
        # Configure search and dynamic tool
        "mcp_search_query": "fetch",
        "mcp_dynamic_tool_name": "fetch",
        "mcp_dynamic_tool_args": {"url": "https://httpbin.org/json"},
        "mcp_dynamic_server_name": "fetch"
    }
    
    flow = create_mcp_comprehensive_flow()
    flow.run(shared)
    
    print("=== MCP Comprehensive Flow Results ===")
    print(f"Servers: {len(shared.get('mcp_servers_info', {}).get('servers', []))}")
    print(f"Tools: {len(shared.get('mcp_tools', []))}")
    print(f"Search matches: {shared.get('mcp_search_results', {}).get('total_matches', 0)}")
    print(f"Final tool result: {shared.get('mcp_dynamic_tool_result', {})}")
    
    return shared


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Running MCP flow examples...")
    
    # Run discovery flow
    print("\n" + "="*50)
    run_discovery_flow()
    
    # Run other flows (commented out to avoid errors if servers aren't available)
    # print("\n" + "="*50)
    # run_file_operations_flow()
    
    # print("\n" + "="*50)
    # run_web_fetch_flow()
    
    # print("\n" + "="*50)
    # run_dynamic_tool_flow()
    
    # print("\n" + "="*50)
    # run_tool_search_flow()
    
    # print("\n" + "="*50)
    # run_comprehensive_flow()
