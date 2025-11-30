import logging

from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger

to_client_logger = get_logger(name="fastmcp.server.context.to_client")
to_client_logger.setLevel(level=logging.DEBUG)

mcp = FastMCP(name="demo-server")


@mcp.tool(
    name="eval",
    description="""
Evaluates a Python expression using eval().
This can run any valid Python code, but it cannot run multiline code, or async code.

It can be used for things like math calculations.""",
)
def _eval(code: str) -> str:
    to_client_logger.info(f"Received request for eval with body: {code}")
    try:
        result = str(eval(code))
        to_client_logger.info(f"Response for eval: {result}")
        return result
    except Exception as e:
        to_client_logger.error(f"Error during eval: {e}")
        raise


@mcp.tool(
    name="get_wade",
    description="""
Fetch the WADE web exam page HTML.
This can be used for getting information about the exam/WADE course, and more.""",
)
def get_wade() -> str:
    # simple demo: fetch and return page HTML (sync for brevity)
    import requests

    r = requests.get("https://profs.info.uaic.ro/sabin.buraga/teach/courses/wade/web-exam.html")
    return r.text


if __name__ == "__main__":
    # choose transport: stdio for local, or streamable-http for remote
    mcp.run(transport="stdio")
