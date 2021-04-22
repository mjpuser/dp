import asyncio
import importlib
import logging
import traceback

import aio_pika

from vertex import service, settings


RABBIT_URL = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}/"
PIPELINE_EXCHANGE = 'pipeline'
META_EXCHANGE = 'meta'


async def run_consumer(func, name):
    connection = await aio_pika.connect_robust(RABBIT_URL)

    async with connection:
        # Create channel
        channel = await connection.channel()

        # Declare exchange
        exchange = await channel.declare_exchange(PIPELINE_EXCHANGE, 'topic')
        meta_exchange = await channel.declare_exchange(META_EXCHANGE, 'topic', durable=True)

        # Declare queue
        queue = await channel.declare_queue(name, auto_delete=True)
        await queue.bind(exchange, f'{name}.#')

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await process_message(meta_exchange, exchange, message, func, name)


async def process_message(meta_exchange, exchange, message, func, name):
    func_config = None
    logging.info(f"in {message.info()['correlation_id']} - {name}")
    try:
        async for out, routing_key in func(func_config, message, **{'meta_exchange':meta_exchange}):
            if out is not None and routing_key is not None:
                await exchange.publish(
                    out,
                    routing_key=routing_key,
                )
                logging.info(f"out {out.info()['correlation_id']} - {name}")
    except Exception as e:
        logging.error('Error processing message')
        traceback.print_exception(type(e), e, e.__traceback__)


def load_func(path):
    mod = '.'.join(path.split('.')[:-1])
    func = path.split('.')[-1]
    return getattr(importlib.import_module(mod), func)


async def start():
    status, funcs = await service.DB('func').get()

    if status >= 400 or not funcs:
        logging.info('No functions to load')
        return

    for func in funcs:
        logging.info(f'Loading `{func["name"]}` function')

    consumers = [run_consumer(load_func(func['name']), func['name'])
                 for func in funcs]
    return await asyncio.gather(*consumers)
