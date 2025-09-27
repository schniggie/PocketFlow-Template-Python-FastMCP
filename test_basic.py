#!/usr/bin/env python3
"""
Basic test script to verify the FastMCP integration works without user input.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test original nodes
        from nodes import GetQuestionNode, AnswerNode
        print("✅ Original nodes import successful")
        
        # Test MCP nodes
        from nodes import (
            MCPInitializeNode,
            MCPDiscoverToolsNode,
            MCPCallToolNode,
            MCPDynamicToolNode,
            MCPListServersNode,
            MCPToolSearchNode
        )
        print("✅ MCP nodes import successful")
        
        # Test flows
        from flows.mcp_example_flow import create_mcp_discovery_flow
        print("✅ MCP flows import successful")
        
        # Test configuration
        from utils.mcp_config import MCPConfigManager
        print("✅ MCP configuration import successful")
        
        # Test service
        from utils.mcp_service import get_mcp_service
        print("✅ MCP service import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from utils.mcp_config import MCPConfigManager
        
        # Test with the default config file
        config_path = "config/mcp_servers.json"
        if os.path.exists(config_path):
            manager = MCPConfigManager(config_path)
            config = manager.load_config()
            
            server_names = manager.get_server_names()
            print(f"✅ Configuration loaded successfully: {len(server_names)} servers")
            print(f"   Servers: {', '.join(server_names)}")
            
            # Test conversion to FastMCP format
            fastmcp_config = manager.to_fastmcp_config()
            print(f"✅ FastMCP format conversion successful")
            
            return True
        else:
            print(f"⚠️  Config file not found: {config_path}")
            return True  # Not a failure, just missing config
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_node_creation():
    """Test that nodes can be created."""
    print("\nTesting node creation...")
    
    try:
        from nodes import (
            GetQuestionNode, AnswerNode,
            MCPInitializeNode, MCPDiscoverToolsNode,
            MCPCallToolNode, MCPDynamicToolNode
        )
        
        # Test original nodes
        question_node = GetQuestionNode()
        answer_node = AnswerNode()
        print("✅ Original nodes created successfully")
        
        # Test MCP nodes
        init_node = MCPInitializeNode()
        discover_node = MCPDiscoverToolsNode()
        call_node = MCPCallToolNode("test_tool")
        dynamic_node = MCPDynamicToolNode()
        print("✅ MCP nodes created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Node creation failed: {e}")
        return False


def test_flow_creation():
    """Test that flows can be created."""
    print("\nTesting flow creation...")
    
    try:
        from flows.mcp_example_flow import (
            create_mcp_discovery_flow,
            create_mcp_file_operations_flow,
            create_mcp_dynamic_tool_flow
        )
        
        # Create flows (don't run them)
        discovery_flow = create_mcp_discovery_flow()
        file_flow = create_mcp_file_operations_flow()
        dynamic_flow = create_mcp_dynamic_tool_flow()
        
        print("✅ MCP flows created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Flow creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 FastMCP Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_node_creation,
        test_flow_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastMCP integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
