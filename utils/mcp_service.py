"""
MCP Service Layer

This module provides a service layer for managing FastMCP clients,
handling connection lifecycle, and providing tool discovery and execution.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from .mcp_config import MCPConfigManager

logger = logging.getLogger(__name__)


@dataclass
class MCPToolInfo:
    """Information about an MCP tool."""
    name: str
    description: str
    server_name: str
    schema: Dict[str, Any]


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""
    name: str
    status: str  # 'connected', 'disconnected', 'error'
    tools: List[MCPToolInfo]
    error_message: Optional[str] = None


class MCPService:
    """Service for managing MCP clients and providing tool access."""
    
    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        """
        Initialize the MCP service.
        
        Args:
            config_manager: Configuration manager instance. If None, creates default.
        """
        self.config_manager = config_manager or MCPConfigManager()
        self._clients: Dict[str, Client] = {}
        self._server_info: Dict[str, MCPServerInfo] = {}
        self._initialized = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the MCP service by loading config and connecting to servers."""
        async with self._lock:
            if self._initialized:
                return
            
            try:
                # Load configuration
                config = self.config_manager.load_config()
                fastmcp_config = self.config_manager.to_fastmcp_config()
                
                logger.info(f"Initializing MCP service with {len(fastmcp_config)} servers")
                
                # Initialize clients for each server
                for server_name, server_config in fastmcp_config.items():
                    await self._initialize_server(server_name, server_config)
                
                self._initialized = True
                logger.info("MCP service initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize MCP service: {e}")
                raise
    
    async def _initialize_server(self, server_name: str, server_config: Dict[str, Any]) -> None:
        """Initialize a single MCP server."""
        try:
            # Create transport for the server
            transport = StdioTransport(
                command=server_config["command"],
                args=server_config["args"],
                env=server_config.get("env"),
                cwd=server_config.get("cwd")
            )
            
            # Create client
            client = Client(transport)
            
            # Store client
            self._clients[server_name] = client
            
            # Initialize server info
            self._server_info[server_name] = MCPServerInfo(
                name=server_name,
                status="disconnected",
                tools=[],
                error_message=None
            )
            
            logger.info(f"Initialized server: {server_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize server {server_name}: {e}")
            self._server_info[server_name] = MCPServerInfo(
                name=server_name,
                status="error",
                tools=[],
                error_message=str(e)
            )
    
    async def connect_all_servers(self) -> None:
        """Connect to all configured MCP servers."""
        if not self._initialized:
            await self.initialize()
        
        connection_tasks = []
        for server_name in self._clients:
            task = asyncio.create_task(self._connect_server(server_name))
            connection_tasks.append(task)
        
        # Wait for all connections to complete
        results = await asyncio.gather(*connection_tasks, return_exceptions=True)
        
        # Log results
        for i, result in enumerate(results):
            server_name = list(self._clients.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to connect to {server_name}: {result}")
    
    async def _connect_server(self, server_name: str) -> None:
        """Connect to a single MCP server and discover its tools."""
        client = self._clients.get(server_name)
        if not client:
            logger.error(f"No client found for server: {server_name}")
            return
        
        try:
            # Connect to the server
            await client.__aenter__()
            
            # Discover tools
            tools = await client.list_tools()
            
            # Convert tools to our format
            tool_infos = []
            for tool in tools:
                tool_info = MCPToolInfo(
                    name=tool.name,
                    description=tool.description or "",
                    server_name=server_name,
                    schema=tool.inputSchema or {}
                )
                tool_infos.append(tool_info)
            
            # Update server info
            self._server_info[server_name] = MCPServerInfo(
                name=server_name,
                status="connected",
                tools=tool_infos,
                error_message=None
            )
            
            logger.info(f"Connected to {server_name}, discovered {len(tool_infos)} tools")
            
        except Exception as e:
            logger.error(f"Failed to connect to server {server_name}: {e}")
            self._server_info[server_name] = MCPServerInfo(
                name=server_name,
                status="error",
                tools=[],
                error_message=str(e)
            )
    
    async def disconnect_all_servers(self) -> None:
        """Disconnect from all MCP servers."""
        disconnect_tasks = []
        for server_name, client in self._clients.items():
            if self._server_info[server_name].status == "connected":
                task = asyncio.create_task(self._disconnect_server(server_name, client))
                disconnect_tasks.append(task)
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        logger.info("Disconnected from all MCP servers")
    
    async def _disconnect_server(self, server_name: str, client: Client) -> None:
        """Disconnect from a single MCP server."""
        try:
            await client.__aexit__(None, None, None)
            self._server_info[server_name].status = "disconnected"
            logger.info(f"Disconnected from {server_name}")
        except Exception as e:
            logger.error(f"Error disconnecting from {server_name}: {e}")
    
    def get_server_info(self) -> List[MCPServerInfo]:
        """Get information about all configured servers."""
        return list(self._server_info.values())
    
    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names."""
        return [
            name for name, info in self._server_info.items()
            if info.status == "connected"
        ]
    
    def get_all_tools(self) -> List[MCPToolInfo]:
        """Get all tools from all connected servers."""
        all_tools = []
        for server_info in self._server_info.values():
            if server_info.status == "connected":
                all_tools.extend(server_info.tools)
        return all_tools
    
    def get_tools_by_server(self, server_name: str) -> List[MCPToolInfo]:
        """Get tools from a specific server."""
        server_info = self._server_info.get(server_name)
        if server_info and server_info.status == "connected":
            return server_info.tools
        return []
    
    def find_tool(self, tool_name: str, server_name: Optional[str] = None) -> Optional[MCPToolInfo]:
        """
        Find a tool by name, optionally from a specific server.
        
        Args:
            tool_name: Name of the tool to find
            server_name: Optional server name to search in
            
        Returns:
            Tool information if found, None otherwise
        """
        if server_name:
            # Search in specific server
            tools = self.get_tools_by_server(server_name)
            for tool in tools:
                if tool.name == tool_name:
                    return tool
        else:
            # Search in all servers
            all_tools = self.get_all_tools()
            for tool in all_tools:
                if tool.name == tool_name:
                    return tool
        
        return None
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        server_name: Optional[str] = None
    ) -> Any:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            server_name: Optional server name. If not provided, searches all servers.
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool is not found or server is not connected
            RuntimeError: If tool execution fails
        """
        # Find the tool
        tool_info = self.find_tool(tool_name, server_name)
        if not tool_info:
            available_tools = [t.name for t in self.get_all_tools()]
            raise ValueError(
                f"Tool '{tool_name}' not found. Available tools: {available_tools}"
            )
        
        # Get the client for the server
        client = self._clients.get(tool_info.server_name)
        if not client:
            raise ValueError(f"No client found for server: {tool_info.server_name}")
        
        # Check if server is connected
        server_info = self._server_info.get(tool_info.server_name)
        if not server_info or server_info.status != "connected":
            raise ValueError(f"Server {tool_info.server_name} is not connected")
        
        try:
            # Call the tool
            result = await client.call_tool(tool_name, arguments)
            logger.info(f"Successfully called tool {tool_name} on {tool_info.server_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise RuntimeError(f"Tool execution failed: {e}")
    
    @asynccontextmanager
    async def managed_service(self):
        """Context manager for the MCP service lifecycle."""
        try:
            await self.initialize()
            await self.connect_all_servers()
            yield self
        finally:
            await self.disconnect_all_servers()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        await self.connect_all_servers()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect_all_servers()


# Global service instance
_mcp_service: Optional[MCPService] = None


def get_mcp_service() -> MCPService:
    """Get the global MCP service instance."""
    global _mcp_service
    if _mcp_service is None:
        _mcp_service = MCPService()
    return _mcp_service


async def initialize_mcp_service(config_path: Optional[str] = None) -> MCPService:
    """Initialize and return the global MCP service."""
    global _mcp_service
    if _mcp_service is None:
        config_manager = MCPConfigManager(config_path) if config_path else None
        _mcp_service = MCPService(config_manager)
    
    await _mcp_service.initialize()
    return _mcp_service


if __name__ == "__main__":
    # Example usage
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        service = MCPService()
        
        async with service:
            # Get server info
            servers = service.get_server_info()
            print(f"Servers: {[s.name for s in servers]}")
            
            # Get all tools
            tools = service.get_all_tools()
            print(f"Available tools: {[t.name for t in tools]}")
            
            # Try to call a tool (example)
            if tools:
                try:
                    result = await service.call_tool(
                        tools[0].name,
                        {}  # Empty arguments for example
                    )
                    print(f"Tool result: {result}")
                except Exception as e:
                    print(f"Tool call failed: {e}")
    
    asyncio.run(main())
