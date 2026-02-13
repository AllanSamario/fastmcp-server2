from fastmcp import FastMCP

def register(mcp: FastMCP):

    @mcp.tool
    def hello_world():
        """
        A simple tool that prints Hello World
        """
        return "Hello World"
