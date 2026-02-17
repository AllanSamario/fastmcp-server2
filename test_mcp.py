import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


SERVERS = {
    "Precious Metals Portfolio AI": {
        "transport": "streamable_http",
        "url": "https://consistent-black-cicada.fastmcp.app/mcp",
        "headers": {
            "Authorization": "Bearer fmcp_X-uDbwSjOGkILXlfpIesn0Usvf39uBOmePXTmPyyC1U"
        }
    }
}


async def run_test():
    client = MultiServerMCPClient(SERVERS)

    tools = await client.get_tools()
    print("Available tools:", [t.name for t in tools])

    analyze_tool = next(
        (t for t in tools if t.name == "analyze_precious_metals"),
        None
    )

    if not analyze_tool:
        print("analyze_precious_metals tool not found!")
        return

    result = await analyze_tool.ainvoke({})
    print("Result:\n", result)

asyncio.run(run_test())
