"""
MCP Configuration Management

This module handles loading and parsing MCP server configurations
from the user's desired JSON format and converting them to FastMCP-compatible format.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    command: str
    args: List[str] = Field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None


class MCPServersConfig(BaseModel):
    """Configuration for all MCP servers."""
    mcpServers: Dict[str, MCPServerConfig]

    @validator('mcpServers')
    def validate_servers(cls, v):
        if not v:
            raise ValueError("At least one MCP server must be configured")
        return v


class MCPConfigManager:
    """Manages MCP server configuration loading and conversion."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the config manager.
        
        Args:
            config_path: Path to the MCP servers configuration file.
                        Defaults to 'config/mcp_servers.json'
        """
        self.config_path = config_path or "config/mcp_servers.json"
        self._config: Optional[MCPServersConfig] = None
    
    def load_config(self) -> MCPServersConfig:
        """
        Load and validate the MCP servers configuration.
        
        Returns:
            Validated MCP servers configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
            json.JSONDecodeError: If config is not valid JSON
        """
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"MCP config file not found: {self.config_path}")
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            self._config = MCPServersConfig(**config_data)
            logger.info(f"Loaded MCP configuration with {len(self._config.mcpServers)} servers")
            return self._config
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in config file: {e}", e.doc, e.pos)
        except Exception as e:
            raise ValueError(f"Invalid MCP configuration: {e}")
    
    def to_fastmcp_config(self) -> Dict[str, Any]:
        """
        Convert the loaded configuration to FastMCP-compatible format.
        
        Returns:
            Dictionary in FastMCP client configuration format
            
        Raises:
            RuntimeError: If no configuration has been loaded
        """
        if not self._config:
            raise RuntimeError("No configuration loaded. Call load_config() first.")
        
        fastmcp_config = {}
        
        for server_name, server_config in self._config.mcpServers.items():
            # Convert to FastMCP format
            fastmcp_server = {
                "command": server_config.command,
                "args": server_config.args
            }
            
            # Add optional fields if present
            if server_config.env:
                fastmcp_server["env"] = server_config.env
            if server_config.cwd:
                fastmcp_server["cwd"] = server_config.cwd
            
            fastmcp_config[server_name] = fastmcp_server
        
        logger.debug(f"Converted config to FastMCP format: {fastmcp_config}")
        return fastmcp_config
    
    def get_server_names(self) -> List[str]:
        """
        Get list of configured server names.
        
        Returns:
            List of server names
            
        Raises:
            RuntimeError: If no configuration has been loaded
        """
        if not self._config:
            raise RuntimeError("No configuration loaded. Call load_config() first.")
        
        return list(self._config.mcpServers.keys())
    
    def get_server_config(self, server_name: str) -> Optional[MCPServerConfig]:
        """
        Get configuration for a specific server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Server configuration or None if not found
            
        Raises:
            RuntimeError: If no configuration has been loaded
        """
        if not self._config:
            raise RuntimeError("No configuration loaded. Call load_config() first.")
        
        return self._config.mcpServers.get(server_name)
    
    @classmethod
    def create_example_config(cls, output_path: str = "config/mcp_servers.json"):
        """
        Create an example MCP servers configuration file.
        
        Args:
            output_path: Path where to create the example config
        """
        example_config = {
            "mcpServers": {
                "mcp-server-fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"]
                },
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
                },
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"]
                },
                "browsermcp": {
                    "command": "npx",
                    "args": ["@browsermcp/mcp@latest"]
                },
                "mcp-sequentialthinking-tools": {
                    "command": "npx",
                    "args": ["-y", "mcp-sequentialthinking-tools"]
                }
            }
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(example_config, f, indent=2)
        
        logger.info(f"Created example MCP config at: {output_path}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create example config if it doesn't exist
    config_path = "config/mcp_servers.json"
    if not os.path.exists(config_path):
        MCPConfigManager.create_example_config(config_path)
    
    # Load and convert config
    manager = MCPConfigManager(config_path)
    try:
        config = manager.load_config()
        fastmcp_config = manager.to_fastmcp_config()
        
        print("Loaded servers:", manager.get_server_names())
        print("FastMCP config:", json.dumps(fastmcp_config, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
