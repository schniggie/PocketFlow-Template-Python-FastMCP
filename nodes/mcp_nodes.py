"""
MCP-enabled PocketFlow Nodes

This module provides PocketFlow nodes that can interact with MCP servers
to discover and execute tools.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from pocketflow import Node
from utils.mcp_service import get_mcp_service, MCPService, MCPToolInfo

logger = logging.getLogger(__name__)


class MCPServiceNode(Node):
    """Base node that provides MCP service access."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mcp_service: Optional[MCPService] = None
    
    def get_mcp_service(self) -> MCPService:
        """Get the MCP service instance."""
        if self._mcp_service is None:
            self._mcp_service = get_mcp_service()
        return self._mcp_service
    
    def run_async(self, coro):
        """Helper to run async code in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)


class MCPInitializeNode(MCPServiceNode):
    """Node to initialize the MCP service and connect to servers."""
    
    def exec(self, _):
        """Initialize MCP service and connect to all servers."""
        logger.info("Initializing MCP service...")
        
        service = self.get_mcp_service()
        
        # Initialize and connect to servers
        self.run_async(service.initialize())
        self.run_async(service.connect_all_servers())
        
        # Get server information
        servers = service.get_server_info()
        connected_servers = [s.name for s in servers if s.status == "connected"]
        error_servers = [s.name for s in servers if s.status == "error"]
        
        result = {
            "total_servers": len(servers),
            "connected_servers": connected_servers,
            "error_servers": error_servers,
            "status": "initialized"
        }
        
        logger.info(f"MCP service initialized: {len(connected_servers)} connected, {len(error_servers)} errors")
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Store initialization result in shared store."""
        shared["mcp_init_result"] = exec_res
        shared["mcp_connected_servers"] = exec_res["connected_servers"]
        return "default"


class MCPDiscoverToolsNode(MCPServiceNode):
    """Node to discover all available MCP tools."""
    
    def exec(self, _):
        """Discover all available tools from connected MCP servers."""
        logger.info("Discovering MCP tools...")
        
        service = self.get_mcp_service()
        
        # Get all tools
        tools = service.get_all_tools()
        
        # Convert to serializable format
        tools_info = []
        for tool in tools:
            tool_dict = {
                "name": tool.name,
                "description": tool.description,
                "server_name": tool.server_name,
                "schema": tool.schema
            }
            tools_info.append(tool_dict)
        
        result = {
            "total_tools": len(tools_info),
            "tools": tools_info,
            "tools_by_server": {}
        }
        
        # Group tools by server
        for tool in tools_info:
            server_name = tool["server_name"]
            if server_name not in result["tools_by_server"]:
                result["tools_by_server"][server_name] = []
            result["tools_by_server"][server_name].append(tool)
        
        logger.info(f"Discovered {len(tools_info)} tools from {len(result['tools_by_server'])} servers")
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Store discovered tools in shared store."""
        shared["mcp_tools"] = exec_res["tools"]
        shared["mcp_tools_by_server"] = exec_res["tools_by_server"]
        return "default"


class MCPCallToolNode(MCPServiceNode):
    """Node to call a specific MCP tool."""
    
    def __init__(self, tool_name: str, server_name: Optional[str] = None, *args, **kwargs):
        """
        Initialize the tool calling node.
        
        Args:
            tool_name: Name of the tool to call
            server_name: Optional server name to call the tool from
        """
        super().__init__(*args, **kwargs)
        self.tool_name = tool_name
        self.server_name = server_name
    
    def prep(self, shared):
        """Prepare tool arguments from shared store."""
        # Look for tool arguments in shared store
        tool_args_key = f"mcp_tool_args_{self.tool_name}"
        if tool_args_key in shared:
            return shared[tool_args_key]
        
        # Look for generic tool arguments
        if "mcp_tool_args" in shared:
            return shared["mcp_tool_args"]
        
        # Default to empty arguments
        return {}
    
    def exec(self, tool_args):
        """Execute the MCP tool."""
        logger.info(f"Calling MCP tool: {self.tool_name} with args: {tool_args}")
        
        service = self.get_mcp_service()
        
        try:
            # Call the tool
            result = self.run_async(
                service.call_tool(self.tool_name, tool_args, self.server_name)
            )
            
            logger.info(f"Tool {self.tool_name} executed successfully")
            return {
                "success": True,
                "tool_name": self.tool_name,
                "server_name": self.server_name,
                "arguments": tool_args,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to call tool {self.tool_name}: {e}")
            return {
                "success": False,
                "tool_name": self.tool_name,
                "server_name": self.server_name,
                "arguments": tool_args,
                "error": str(e)
            }
    
    def post(self, shared, prep_res, exec_res):
        """Store tool result in shared store."""
        # Store result with tool-specific key
        result_key = f"mcp_tool_result_{self.tool_name}"
        shared[result_key] = exec_res
        
        # Also store in generic result key
        shared["mcp_last_tool_result"] = exec_res
        
        # Return action based on success
        if exec_res["success"]:
            return "success"
        else:
            return "error"


class MCPDynamicToolNode(MCPServiceNode):
    """Node that can call any MCP tool based on shared store configuration."""
    
    def prep(self, shared):
        """Prepare tool name and arguments from shared store."""
        tool_name = shared.get("mcp_dynamic_tool_name")
        tool_args = shared.get("mcp_dynamic_tool_args", {})
        server_name = shared.get("mcp_dynamic_server_name")
        
        if not tool_name:
            raise ValueError("mcp_dynamic_tool_name must be set in shared store")
        
        return {
            "tool_name": tool_name,
            "tool_args": tool_args,
            "server_name": server_name
        }
    
    def exec(self, prep_data):
        """Execute the dynamically specified MCP tool."""
        tool_name = prep_data["tool_name"]
        tool_args = prep_data["tool_args"]
        server_name = prep_data["server_name"]
        
        logger.info(f"Calling dynamic MCP tool: {tool_name} with args: {tool_args}")
        
        service = self.get_mcp_service()
        
        try:
            # Call the tool
            result = self.run_async(
                service.call_tool(tool_name, tool_args, server_name)
            )
            
            logger.info(f"Dynamic tool {tool_name} executed successfully")
            return {
                "success": True,
                "tool_name": tool_name,
                "server_name": server_name,
                "arguments": tool_args,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to call dynamic tool {tool_name}: {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "server_name": server_name,
                "arguments": tool_args,
                "error": str(e)
            }
    
    def post(self, shared, prep_res, exec_res):
        """Store dynamic tool result in shared store."""
        shared["mcp_dynamic_tool_result"] = exec_res
        shared["mcp_last_tool_result"] = exec_res
        
        # Return action based on success
        if exec_res["success"]:
            return "success"
        else:
            return "error"


class MCPListServersNode(MCPServiceNode):
    """Node to list all MCP servers and their status."""
    
    def exec(self, _):
        """List all MCP servers and their connection status."""
        logger.info("Listing MCP servers...")
        
        service = self.get_mcp_service()
        servers = service.get_server_info()
        
        servers_info = []
        for server in servers:
            server_dict = {
                "name": server.name,
                "status": server.status,
                "tool_count": len(server.tools),
                "tools": [tool.name for tool in server.tools],
                "error_message": server.error_message
            }
            servers_info.append(server_dict)
        
        result = {
            "total_servers": len(servers_info),
            "servers": servers_info,
            "connected_count": len([s for s in servers_info if s["status"] == "connected"]),
            "error_count": len([s for s in servers_info if s["status"] == "error"])
        }
        
        logger.info(f"Listed {len(servers_info)} MCP servers")
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Store server list in shared store."""
        shared["mcp_servers_info"] = exec_res
        return "default"


class MCPToolSearchNode(MCPServiceNode):
    """Node to search for tools by name or description."""
    
    def prep(self, shared):
        """Get search query from shared store."""
        search_query = shared.get("mcp_search_query", "")
        if not search_query:
            raise ValueError("mcp_search_query must be set in shared store")
        return search_query.lower()
    
    def exec(self, search_query):
        """Search for tools matching the query."""
        logger.info(f"Searching for MCP tools with query: {search_query}")
        
        service = self.get_mcp_service()
        all_tools = service.get_all_tools()
        
        # Search in tool names and descriptions
        matching_tools = []
        for tool in all_tools:
            if (search_query in tool.name.lower() or 
                search_query in tool.description.lower()):
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "server_name": tool.server_name,
                    "schema": tool.schema
                }
                matching_tools.append(tool_dict)
        
        result = {
            "search_query": search_query,
            "total_matches": len(matching_tools),
            "matching_tools": matching_tools
        }
        
        logger.info(f"Found {len(matching_tools)} tools matching '{search_query}'")
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Store search results in shared store."""
        shared["mcp_search_results"] = exec_res
        return "default"


if __name__ == "__main__":
    # Example usage of MCP nodes
    logging.basicConfig(level=logging.INFO)
    
    # Test the nodes
    shared = {}
    
    # Initialize MCP service
    init_node = MCPInitializeNode()
    init_result = init_node.exec(None)
    init_node.post(shared, None, init_result)
    print("Initialization result:", init_result)
    
    # Discover tools
    discover_node = MCPDiscoverToolsNode()
    discover_result = discover_node.exec(None)
    discover_node.post(shared, None, discover_result)
    print("Discovery result:", discover_result)
    
    # List servers
    list_node = MCPListServersNode()
    list_result = list_node.exec(None)
    list_node.post(shared, None, list_result)
    print("Server list result:", list_result)
