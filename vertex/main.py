import asyncio
from vertex import daemon

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(daemon.start())
    loop.close()
