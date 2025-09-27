"""
Tests for MCP Configuration Management
"""

import json
import os
import tempfile
import pytest
from pathlib import Path

from utils.mcp_config import MCPConfigManager, MCPServerConfig, MCPServersConfig


class TestMCPServerConfig:
    """Test MCPServerConfig model."""
    
    def test_basic_config(self):
        """Test basic server configuration."""
        config = MCPServerConfig(
            command="uvx",
            args=["mcp-server-fetch"]
        )
        
        assert config.command == "uvx"
        assert config.args == ["mcp-server-fetch"]
        assert config.env is None
        assert config.cwd is None
    
    def test_full_config(self):
        """Test server configuration with all fields."""
        config = MCPServerConfig(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            env={"NODE_ENV": "production"},
            cwd="/app"
        )
        
        assert config.command == "npx"
        assert config.args == ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        assert config.env == {"NODE_ENV": "production"}
        assert config.cwd == "/app"


class TestMCPServersConfig:
    """Test MCPServersConfig model."""
    
    def test_valid_config(self):
        """Test valid servers configuration."""
        config_data = {
            "mcpServers": {
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"]
                }
            }
        }
        
        config = MCPServersConfig(**config_data)
        assert "fetch" in config.mcpServers
        assert config.mcpServers["fetch"].command == "uvx"
    
    def test_empty_servers_invalid(self):
        """Test that empty servers configuration is invalid."""
        config_data = {"mcpServers": {}}
        
        with pytest.raises(ValueError, match="At least one MCP server must be configured"):
            MCPServersConfig(**config_data)


class TestMCPConfigManager:
    """Test MCPConfigManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        
        # Create a test configuration
        self.test_config = {
            "mcpServers": {
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"]
                },
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                    "env": {"NODE_ENV": "test"}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)
    
    def test_load_config_success(self):
        """Test successful configuration loading."""
        manager = MCPConfigManager(self.config_path)
        config = manager.load_config()
        
        assert isinstance(config, MCPServersConfig)
        assert len(config.mcpServers) == 2
        assert "fetch" in config.mcpServers
        assert "filesystem" in config.mcpServers
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file."""
        manager = MCPConfigManager("nonexistent.json")
        
        with pytest.raises(FileNotFoundError):
            manager.load_config()
    
    def test_load_config_invalid_json(self):
        """Test loading invalid JSON configuration."""
        invalid_config_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_config_path, 'w') as f:
            f.write("{ invalid json }")
        
        manager = MCPConfigManager(invalid_config_path)
        
        with pytest.raises(json.JSONDecodeError):
            manager.load_config()
        
        os.remove(invalid_config_path)
    
    def test_to_fastmcp_config(self):
        """Test conversion to FastMCP format."""
        manager = MCPConfigManager(self.config_path)
        manager.load_config()
        
        fastmcp_config = manager.to_fastmcp_config()
        
        assert "fetch" in fastmcp_config
        assert "filesystem" in fastmcp_config
        
        fetch_config = fastmcp_config["fetch"]
        assert fetch_config["command"] == "uvx"
        assert fetch_config["args"] == ["mcp-server-fetch"]
        assert "env" not in fetch_config  # Should not include None values
        
        filesystem_config = fastmcp_config["filesystem"]
        assert filesystem_config["command"] == "npx"
        assert filesystem_config["args"] == ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        assert filesystem_config["env"] == {"NODE_ENV": "test"}
    
    def test_to_fastmcp_config_without_loading(self):
        """Test conversion without loading configuration first."""
        manager = MCPConfigManager(self.config_path)
        
        with pytest.raises(RuntimeError, match="No configuration loaded"):
            manager.to_fastmcp_config()
    
    def test_get_server_names(self):
        """Test getting server names."""
        manager = MCPConfigManager(self.config_path)
        manager.load_config()
        
        server_names = manager.get_server_names()
        
        assert len(server_names) == 2
        assert "fetch" in server_names
        assert "filesystem" in server_names
    
    def test_get_server_config(self):
        """Test getting specific server configuration."""
        manager = MCPConfigManager(self.config_path)
        manager.load_config()
        
        fetch_config = manager.get_server_config("fetch")
        assert fetch_config is not None
        assert fetch_config.command == "uvx"
        
        nonexistent_config = manager.get_server_config("nonexistent")
        assert nonexistent_config is None
    
    def test_create_example_config(self):
        """Test creating example configuration."""
        example_path = os.path.join(self.temp_dir, "example.json")
        
        MCPConfigManager.create_example_config(example_path)
        
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            example_config = json.load(f)
        
        assert "mcpServers" in example_config
        assert len(example_config["mcpServers"]) > 0
        
        # Check that it's valid
        config = MCPServersConfig(**example_config)
        assert len(config.mcpServers) > 0
        
        os.remove(example_path)


if __name__ == "__main__":
    pytest.main([__file__])
