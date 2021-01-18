import asyncio
import logging

import aio_pika
from aiohttp_requests import requests

from vertex import settings


RABBIT_URL = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}/"
LOGGER = logging.getLogger(__name__)


async def run_consumer(queue_name, routing_key_in, routing_key_out):
    connection = await aio_pika.connect_robust(RABBIT_URL)

    async with connection:
        # Creating channel
        channel = await connection.channel()

        exchange = await channel.declare_exchange('pipeline', 'topic')

        # Declaring queue
        queue = await channel.declare_queue(queue_name, auto_delete=False)
        await queue.bind(exchange, routing_key_in)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    LOGGER.info(message.body)
                    await exchange.publish(
                        aio_pika.Message(body=message.body),
                        routing_key=routing_key_out,
                    )


async def load_config():
    response = await requests.get('http://rest:3000/pipeline')
    config = await response.json()
    return config


async def start():
    config = await load_config()
    consumers = [run_consumer(vertex['name'], vertex['routing_key_in'], vertex['routing_key_out']) for vertex in config]
    return await asyncio.gather(*consumers)        
