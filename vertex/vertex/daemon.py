import asyncio
import logging
import sys

import aio_pika
from aiohttp_requests import requests

from vertex import settings


RABBIT_URL = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}/"


async def run_consumer(queue_id, pipeline_id, routing_key_in, routing_key_out,
                       exchange_name_in='pipeline', exchange_name_out='pipeline'):
    connection = await aio_pika.connect_robust(RABBIT_URL)

    async with connection:
        # Create channel
        channel = await connection.channel()

        # Declare exchange
        exchange_in = exchange_out = await channel.declare_exchange(exchange_name_in, 'topic')
        if exchange_name_in != exchange_name_out:
            exchange_out = await channel.declare_exchange(exchange_name_out, 'topic')

        # Declare queue
        queue = await channel.declare_queue(queue_id, auto_delete=True)
        await queue.bind(exchange_in, routing_key_in)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logging.info(f'{pipeline_id}:{queue_id}:{routing_key_in}:{routing_key_out} `{message.body}`')
                    await exchange_out.publish(
                        aio_pika.Message(body=message.body),
                        routing_key=routing_key_out,
                    )


async def load_vertices():
    response = await requests.get(f'{settings.REST_URL}/vertex')
    data = await response.json()
    if response.status < 400:
        return data
    else:
        logging.warn('Error loading vertex config: %s', data['message'])
        return []


async def start():
    vertices = await load_vertices()

    for vertex in vertices:
        logging.info(f'Loading `{vertex["name"]}` vertex')

    consumers = [
        run_consumer(
            vertex['id'],
            vertex['pipeline_id'],
            vertex['routing_key_in'],
            vertex['routing_key_out']) for vertex in vertices]
    return await asyncio.gather(*consumers)        
