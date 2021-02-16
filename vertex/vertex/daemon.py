import asyncio
import importlib
import json
import logging
import traceback

import aio_pika

from vertex import service, settings


RABBIT_URL = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}/"
PIPELINE_EXCHANGE = 'pipeline'


async def run_consumer(vertex_id, pipeline_id, exchange_name_in, routing_key_in,
                       func, func_config):
    connection = await aio_pika.connect_robust(RABBIT_URL)

    async with connection:
        # Create channel
        channel = await connection.channel()

        # Declare exchange
        exchange_in = exchange_out = await channel.declare_exchange(exchange_name_in, 'topic')
        if exchange_name_in != PIPELINE_EXCHANGE:
            exchange_out = await channel.declare_exchange(PIPELINE_EXCHANGE, 'topic')

        # Declare queue
        queue = await channel.declare_queue(vertex_id, auto_delete=True)
        await queue.bind(exchange_in, routing_key_in)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logging.info(f'{vertex_id}:{pipeline_id}:{exchange_name_in}:{routing_key_in} `{message.body}`')
                    await process_message(message, exchange_out, vertex_id, func, func_config)


async def process_message(message, exchange_out, vertex_id, func, func_config):
    body = json.loads(message.body)
    try:
        async for out, routing_key in func(func_config, body):
            if out is not None:
                await exchange_out.publish(
                    aio_pika.Message(body=out),
                    routing_key=(routing_key or vertex_id).format(vertex_id=vertex_id),
                )
    except Exception as e:
        logging.error('Error processing message')
        traceback.print_exception(type(e), e, e.__traceback__)


def load_func(path):
    mod = '.'.join(path.split('.')[:-1])
    func = path.split('.')[-1]
    return getattr(importlib.import_module(mod), func)


async def start():
    status, vertices = await service.DB('vertex').get()

    if status >= 400 or not vertices:
        logging.info('No vertices to load')
        return

    for vertex in vertices:
        logging.info(f'Loading `{vertex["name"]}` vertex')

    consumers = [
        run_consumer(
            '{vertex[id]}.{vertex[name]}'.format(vertex=vertex),
            vertex['pipeline_id'],
            vertex['exchange_in'],
            vertex['routing_key_in'],
            load_func(vertex['func']),
            vertex['func_config']) for vertex in vertices]
    return await asyncio.gather(*consumers)        
