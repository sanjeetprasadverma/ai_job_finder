"""
MCP server for AI Job Finder.
 
Exposes job search as a tool that any MCP-compatible client
 
Run locally with:
    mcp dev MCP/server.py
 
Run as a standalone stdio server:
    python MCP/server.py
"""
 
from mcp.server.mcpserver import MCPServer
from utils.apis import get_jobs_db  
from common.logger import mcp_logger

mcp = MCPServer("ai-job-finder")
 

@mcp.tool()
def search_jobs(query: str, page: int = 1, pagesize: int = 10, distance: float = 0.9) -> dict:
    """
    Search job postings by natural-language query using vector similarity search.
 
    Args:
        query: What kind of job to search for, e.g. "senior python developer remote".
        page: Page number for pagination, starting at 1.
        pagesize: Number of results to return per page.
        distance: Minimum similarity distance threshold (lower = stricter match).
 
    Returns:
        A dict with "status" (200 on success) and "message" (list of matching jobs,
        or a string if no results / on error).
    """
    mcp_logger.info(f"search_jobs tool called")
    return get_jobs_db(query, page=page, pagesize=pagesize, distance=distance)
 
 
# if __name__ == "__main__":
#     mcp.run(transport="stdio")

if __name__ == "__main__":
    mcp.run(transport="streamable-http",  host="0.0.0.0", port=8000)