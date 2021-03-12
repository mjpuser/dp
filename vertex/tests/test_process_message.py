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


routing_keys = ['routing_key', None]

@pytest.mark.asyncio
@pytest.mark.parametrize("routing_key", routing_keys)
async def test_routing_key(routing_key, exchange):
    msg_in = Mock(aio_pika.message.Message)
    msg_in.info.return_value = {'correlation_id': 'test'}
    msg_out = Mock(aio_pika.message.Message)

    async def func(config, body):
        yield msg_out, routing_key

    await process_message(exchange, msg_in, func, 'func')

    if routing_key is not None:
        exchange.publish.assert_called_with(msg_out, routing_key=routing_key)
    if routing_key is None:
        exchange.publish.assert_not_called()


messages = [Mock(aio_pika.message.Message), None]

@pytest.mark.asyncio
@pytest.mark.parametrize("msg", messages)
async def test_msg(msg, exchange):
    routing_key = 'test'

    msg_in = Mock(aio_pika.message.Message)
    msg_in.info.return_value = {'correlation_id': 'test'}

    async def func(config, body):
        yield msg, routing_key
    await process_message(exchange, msg_in, func, 'func')

    if msg is not None:
        exchange.publish.assert_called_with(msg, routing_key=routing_key)
    if msg is None:
        exchange.publish.assert_not_called()
