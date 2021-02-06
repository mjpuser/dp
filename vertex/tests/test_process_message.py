import json
from unittest.mock import Mock

import aio_pika
import pytest

from vertex.daemon import process_message


@pytest.fixture(scope="function", autouse=True)
def setup(monkeypatch):
    def eq(self, other):
        return self.body == other.body
    monkeypatch.setattr(aio_pika.Message, '__eq__', eq)

    def mock_json_loads(*args):
        return {'test': 1}
    monkeypatch.setattr(json, 'loads', mock_json_loads)


@pytest.fixture
def exchange(*args, **kwargs):
    return Mock(aio_pika.exchange.Exchange)


@pytest.mark.asyncio
async def test_routing_key(monkeypatch, exchange):
    routing_key = 'routing_key'
    output = b'output'
    async def func(config, body):
        yield output, routing_key

    msg = Mock(aio_pika.message.Message)
    vertex_id = 'vertex_id'

    await process_message(msg, exchange, vertex_id, func, {})

    exchange.publish.assert_called_with(aio_pika.Message(body=output), routing_key=routing_key)


@pytest.mark.asyncio
async def test_routing_key_fallback(monkeypatch, exchange):
    routing_key = None
    output = b'output'
    async def func(config, body):
        yield output, routing_key

    msg = Mock(aio_pika.message.Message)
    vertex_id = 'vertex_id'

    await process_message(msg, exchange, vertex_id, func, {})

    exchange.publish.assert_called_with(aio_pika.Message(body=output), routing_key=vertex_id)


@pytest.mark.asyncio
async def test_routing_key_format(monkeypatch, exchange):
    routing_key = '{vertex_id}.test'
    output = b'output'
    async def func(config, body):
        yield output, routing_key

    msg = Mock(aio_pika.message.Message)
    vertex_id = 'vertex_id'

    await process_message(msg, exchange, vertex_id, func, {})

    exchange.publish.assert_called_with(aio_pika.Message(body=output), routing_key=f'{vertex_id}.test')
