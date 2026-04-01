import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_server import handle_list_tools

@pytest.mark.asyncio
async def test_mcp_server_reachable_and_tools_discovered():
    """
    MCP Health Check: A Ping test that ensures the MCP Server is reachable 
    and all tools are discovered before the UI starts.
    """
    tools = await handle_list_tools()
    
    # Assert we received a list of tools
    assert tools is not None
    assert len(tools) >= 4
    
    # Verify expected tools are registered
    tool_names = [t.name for t in tools]
    assert "fetch_vendors" in tool_names
    assert "post_bid" in tool_names
    assert "get_ticket_context" in tool_names
    assert "update_status" in tool_names
    
    print("MCP Server health check passed. Tools discovered successfully.")
