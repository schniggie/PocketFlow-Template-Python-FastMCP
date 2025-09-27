import logging
import os
from flow import create_qa_flow
from flows.mcp_example_flow import (
    create_mcp_discovery_flow,
    run_discovery_flow,
    run_comprehensive_flow
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_original_qa_flow():
    """Run the original Q&A flow."""
    print("\n" + "="*60)
    print("RUNNING ORIGINAL Q&A FLOW")
    print("="*60)
    
    shared = {
        "question": "In one sentence, what's the end of universe?",
        "answer": None
    }

    qa_flow = create_qa_flow()
    qa_flow.run(shared)
    print("Question:", shared["question"])
    print("Answer:", shared["answer"])
    
    return shared


def run_mcp_demo():
    """Run MCP demonstration flows."""
    print("\n" + "="*60)
    print("RUNNING MCP DEMONSTRATION")
    print("="*60)
    
    try:
        # Run MCP discovery flow
        print("\n--- MCP Discovery Flow ---")
        discovery_result = run_discovery_flow()
        
        # If we have connected servers, run comprehensive flow
        connected_servers = discovery_result.get('mcp_connected_servers', [])
        if connected_servers:
            print(f"\nFound {len(connected_servers)} connected servers: {connected_servers}")
            print("\n--- MCP Comprehensive Flow ---")
            run_comprehensive_flow()
        else:
            print("\nNo MCP servers connected. Check your configuration and server availability.")
            print("Available servers in config:")
            servers_info = discovery_result.get('mcp_servers_info', {})
            for server in servers_info.get('servers', []):
                print(f"  - {server['name']}: {server['status']}")
                if server.get('error_message'):
                    print(f"    Error: {server['error_message']}")
    
    except Exception as e:
        logger.error(f"MCP demonstration failed: {e}")
        print(f"MCP demonstration failed: {e}")
        print("\nThis is expected if MCP servers are not properly configured or available.")
        print("To fix this:")
        print("1. Ensure the MCP servers in config/mcp_servers.json are installed")
        print("2. Check that the commands (uvx, npx) are available in your environment")
        print("3. Run with docker-compose for a complete environment")


def main():
    """Main function demonstrating both original and MCP functionality."""
    print("PocketFlow Template with FastMCP Integration")
    print("=" * 60)
    
    # Check if we should run MCP demo
    run_mcp = os.getenv("RUN_MCP_DEMO", "true").lower() == "true"
    
    if run_mcp:
        # Run MCP demonstration first
        run_mcp_demo()
    
    # Run original Q&A flow
    run_original_qa_flow()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nTo explore more MCP functionality:")
    print("1. Check out flows/mcp_example_flow.py for more examples")
    print("2. Modify config/mcp_servers.json to add your own MCP servers")
    print("3. Create custom nodes using nodes/mcp_nodes.py as a reference")
    print("4. Run tests with: docker-compose run test")


if __name__ == "__main__":
    main()
