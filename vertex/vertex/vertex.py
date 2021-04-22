import base64
import difflib
import functools
import json
import logging
from typing import Optional
import uuid

import aio_pika

from vertex import service
from vertex import settings


async def get_receiver(sender_id: uuid.UUID):
    params = {
        'select': 'vertex.receiver(id,func)', 'sender': f'eq.{sender_id}'}
    status, connections = await service.DB('vertex_connection').get(params=params)
    return status, connections


def wrap_correlation_id(data: Optional[bytes]) -> bytes:
    return base64.b64encode(data or uuid.uuid4().bytes)


def unwrap_correlation_id(correlation_id: bytes) -> Optional[bytes]:
    if len(correlation_id) == 16:
        return None
    return base64.b64decode(correlation_id)


def report_diff(f):
    d = difflib.Differ()

    @functools.wraps(f)
    async def wrapper(config, msg_in, meta_exchange=None):
        async for msg_out, key_out in f(config, msg_in):
            yield msg_out, key_out
            a = json.dumps(json.loads(msg_in.body), indent=2).splitlines()
            b = json.dumps(json.loads(msg_out.body), indent=2).splitlines()
            patch = '\n'.join(list(d.compare(a, b)))
            headers = {'actor': msg_in.headers['receiver_id'],
                       'correlation_id': msg_in.info()['correlation_id']}
            diff_msg = aio_pika.Message(body=patch.encode('utf-8'), headers=headers)
            await meta_exchange.publish(diff_msg, routing_key='test')

    return wrapper


@report_diff
async def filter(config, message, **kwargs):
    my_id = message.headers["receiver_id"]
    status, vertex = await service.DB('vertex').get(params={'select': 'func_config',
                                                            'id': f'eq.{my_id}'},
                                                    headers={'accept': 'application/vnd.pgrst.object+json'})
    status, receivers = await get_receiver(my_id)
    fields = vertex['func_config']['fields']
    body = json.loads(message.body)
    filtered = {field: body.get(field) for field in fields}

    for receiver in receivers:
        headers = {
            'dataset': message.headers.get('dataset'),
            'sender_id': message.headers['receiver_id'],
            'pipeline_id': message.headers['pipeline_id'],
            'receiver_id': receiver['vertex']['id'],
        }
        out = aio_pika.Message(
            body=json.dumps(filtered).encode('utf-8'),
            headers=headers,
            correlation_id=f"{message.info()['correlation_id']}")
        yield out, receiver['vertex']['func']
