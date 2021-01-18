
import asyncio
import logging
from vertex import daemon

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting vertex')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(daemon.start())
    loop.close()
