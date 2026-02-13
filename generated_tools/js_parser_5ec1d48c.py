from fastmcp import FastMCP

def register(mcp: FastMCP):

    @mcp.tool
    def js_parser():
        """
        A simple tool that parse json code
        """
        return "Hello World"
