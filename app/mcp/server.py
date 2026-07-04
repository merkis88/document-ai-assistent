from mcp.server.fastmcp import FastMCP

from app.core.config import MCP_SERVER_NAME
from app.mcp.tools.documents import register_document_tools


mcp = FastMCP(MCP_SERVER_NAME)

register_document_tools(mcp)


if __name__ == "__main__":
    mcp.run()