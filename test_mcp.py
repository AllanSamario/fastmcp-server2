import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

# Your actual Horizon deployment URL
SERVERS = {
    "Precious Metals Portfolio AI": {
        "transport": "streamable_http",
        "url": "https://consistent-black-cicada.fastmcp.app/mcp",
        "headers": {
            "Authorization": "Bearer YOUR_TOKEN_HERE"
        }
    }
}

async def run_test():
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    
    # Let's find and call the AI tool specifically
    ai_tool = next((t for t in tools if t.name == "generate_ai_analysis"), None)
    
    if ai_tool:
        print("Calling AI Analysis Tool...")
        result = await ai_tool.ainvoke({})
        # The result is usually a list of dicts. We want the text from the first one.
        print("\n--- AI FINANCIAL ADVICE ---")
        print(result[0]["text"])
    else:
        print("Tool not found. Current tools:", [t.name for t in tools])

if __name__ == "__main__":
    asyncio.run(run_test())