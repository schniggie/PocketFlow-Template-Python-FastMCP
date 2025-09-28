#!/usr/bin/env python3
"""
Setup script for PocketFlow Template with FastMCP Integration
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required, but you have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} is compatible")
    return True

def check_dependencies():
    """Check if required system dependencies are available."""
    dependencies = {
        "node": "Node.js (for MCP servers)",
        "npm": "npm (for MCP servers)", 
        "docker": "Docker (optional, for containerized development)"
    }
    
    missing = []
    for cmd, desc in dependencies.items():
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            print(f"✅ {desc} is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            if cmd == "docker":
                print(f"⚠️  {desc} not found (optional)")
            else:
                print(f"❌ {desc} not found")
                missing.append(cmd)
    
    return len(missing) == 0

def install_python_dependencies():
    """Install Python dependencies."""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def test_installation():
    """Test that the installation works."""
    print("\n🧪 Testing installation...")
    
    # Test basic imports
    test_commands = [
        ("python -c 'import pocketflow; print(\"PocketFlow imported successfully\")'", "PocketFlow import"),
        ("python -c 'import fastmcp; print(\"FastMCP imported successfully\")'", "FastMCP import"),
        ("python -c 'from nodes import GetQuestionNode, AnswerNode; print(\"Nodes imported successfully\")'", "Node imports"),
        ("python test_basic.py", "Running test suite")
    ]
    
    all_passed = True
    for cmd, desc in test_commands:
        if not run_command(cmd, desc):
            all_passed = False
    
    return all_passed

def main():
    """Main setup function."""
    print("🚀 PocketFlow Template with FastMCP Integration Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check system dependencies
    print("\n📋 Checking system dependencies...")
    if not check_dependencies():
        print("\n⚠️  Some system dependencies are missing.")
        print("Please install Node.js and npm to use MCP servers.")
        print("Visit: https://nodejs.org/")
    
    # Install Python dependencies
    print("\n📦 Installing Python dependencies...")
    if not install_python_dependencies():
        print("\n❌ Failed to install Python dependencies")
        print("Try running manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed")
        print("Please check the error messages above")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📚 Next steps:")
    print("1. Configure your MCP servers in config/mcp_servers.json")
    print("2. Set your OPENAI_API_KEY environment variable")
    print("3. Run: python main.py")
    print("4. Or use Docker: docker-compose up app")
    print("\n🧪 Run tests with: python test_basic.py")

if __name__ == "__main__":
    main()
