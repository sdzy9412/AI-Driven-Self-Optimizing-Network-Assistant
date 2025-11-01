import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def test_mcp_server():
    """Test local MCP server following AWS tutorial pattern"""
    
    mcp_url = "http://localhost:8000/mcp"
    headers = {}

    try:
        async with streamablehttp_client(mcp_url, headers, timeout=30) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # List available tools
                tool_result = await session.list_tools()
                print("🔧 Available MCP Tools:")
                for tool in tool_result.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test traffic_steering
                print("\n🧪 Testing traffic_steering...")
                result = await session.call_tool("traffic_steering", {
                    "cell_id": "cell-A01",
                    "steering_percentage": 40,
                    "backup_path_priority": "high"
                })
                print(f"Result: {result.content[0].text}")
                
                # Test load_balancing
                print("\n🧪 Testing load_balancing...")
                result = await session.call_tool("load_balancing", {
                    "cell_id": "cell-B17",
                    "load_reduction_pct": 25,
                    "target_utilization": 70
                })
                print(f"Result: {result.content[0].text}")
                
                # Test network_health_check
                print("\n🧪 Testing network_health_check...")
                result = await session.call_tool("network_health_check", {
                    "cell_ids": ["cell-A01", "cell-B17"]
                })
                print(f"Result: {result.content[0].text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure MCP server is running: python network_mcp_server.py")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())