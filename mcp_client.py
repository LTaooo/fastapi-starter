import traceback

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def main():
    transport = StreamableHttpTransport('http://180.184.146.229:8087/mcp')
    # transport = StreamableHttpTransport("https://remote.mcpservers.org/fetch/mcp")
    # transport = StreamableHttpTransport("http://127.0.0.1:8000/mcp")
    # transport = StreamableHttpTransport("https://www.xqcrm.com/test/mcp")
    try:
        async with Client(transport=transport) as client:
            print(await client.list_tools())
    except Exception as e:
        traceback.print_exc()
        print(e)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
