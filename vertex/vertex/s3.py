import json
import logging
import traceback
import urllib
import uuid

import aio_pika
import aiohttp

from vertex import service
from vertex.vertex import get_receiver


def get_dataset_name(key: str) -> str:
    return key.split('/')[0]


async def split(config, message):
    body = json.loads(message.body)
    event_name = body.get('EventName', '')
    if not event_name.startswith('s3:ObjectCreated'):
        logging.info(
            f'Skip processing event `{event_name}`.  Must be an s3:ObjectCreated* event')
        return

    bucket = body['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote(body['Records'][0]['s3']['object']['key'])
    content_type = body['Records'][0]['s3']['object']['contentType']

    if content_type != 'text/csv':
        logging.info(
            f'Skip processing file {bucket}/{key} since content type is {content_type}.  File must be a CSV to process')
        return

    async with service.s3() as s3:
        res = await s3.select_object_content(
            Bucket=bucket,
            Key=key,
            Expression='SELECT * FROM S3Object',
            ExpressionType='SQL',
            InputSerialization={
                'CSV': {
                    'FileHeaderInfo': 'USE',
                    'FieldDelimiter': ',',
                    'QuoteCharacter': '"',
                },
                'CompressionType': 'NONE',  # 'NONE'|'GZIP'|'BZIP2',d
            },
            OutputSerialization={'JSON': {}},
        )
        status, receivers = await get_receiver(message.headers['receiver_id'])
        if status >= 400:
            return
        event_stream = res['Payload']
        # Iterate over events in the event stream as they come
        async for event in event_stream:
            # If we received a records event, write the data to a file
            if 'Records' in event:
                data = event['Records']['Payload'].decode(
                    'utf-8').strip().split('\n')
                for datum in data:
                    for receiver in receivers:
                        headers = {
                            'dataset': message.headers.get('dataset'),
                            'sender_id': message.headers['receiver_id'],
                            'pipeline_id': message.headers['pipeline_id'],
                            'receiver_id': receiver['vertex']['id'],
                        }
                        out = aio_pika.Message(
                            body=datum.encode('utf-8'),
                            headers=headers,
                            correlation_id=f"{message.info()['correlation_id']}_{str(uuid.uuid4())}")
                        yield out, receiver['vertex']['func']
            elif 'End' in event:
                end_event_received = True
        if not end_event_received:
            raise Exception("End event not received, request incomplete.")
        event_stream.close()


async def register_dataset(config, message):
    body = json.loads(message.body)
    event_name = body.get('EventName', '')
    if not event_name.startswith('s3:ObjectCreated'):
        logging.info(
            f'Skip processing event `{event_name}`.  Must be an s3:ObjectCreated* event')
        return

    key = urllib.parse.unquote(body['Records'][0]['s3']['object']['key'])
    name = get_dataset_name(key)
    dataset_client = service.DB('dataset')
    status, _ = await dataset_client.post(data={'name': name})
    if status < 400 or 409:
        logging.info(f'Dataset {name} already added')
    else:
        logging.error(f'Dataset {name} failed to add')
        return
    status, pipeline = await service.DB('pipeline').get(params={'select': 'id,vertex(id,func,vertex_connection.sender(receiver(id,func)))',
                                                                'name': 'eq.dataset',
                                                                'vertex.func': 'eq.vertex.s3.register_dataset'},
                                                        headers={'accept': 'application/vnd.pgrst.object+json'})
    if status < 400:
        out = aio_pika.Message(body=message.body, headers={
            'sender_id': pipeline['vertex'][0]['id'],
            'pipeline_id': pipeline['id'],
            'receiver_id': pipeline['vertex'][0]['vertex_connection'][0]['receiver']['id'],
            'dataset': name},
            correlation_id=str(uuid.uuid4()))
        yield out, pipeline['vertex'][0]['vertex_connection'][0]['receiver']['func']
    else:
        logging.error('Unable to find dataset pipeline')
        return


async def write(config, message):
    status, vertex = await service.DB('vertex').get(params={'select': 'func_config',
                                                            'id': f'eq.{message.headers["receiver_id"]}'},
                                                    headers={'accept': 'application/vnd.pgrst.object+json'})
    body = json.loads(message.body)
    status, receivers = await get_receiver(message.headers['receiver_id'])
    async with service.s3() as s3:
        try:
            await s3.put_object(
                Body=json.dumps(body).encode('utf-8'),
                Bucket=vertex['func_config']['bucket'],
                Key=vertex['func_config']['key'].format(message={**{'id': str(uuid.uuid4())}, **body}, path=message.headers.get('dataset')))
        except aiohttp.client_exceptions.ClientConnectionError as e:
            # dunno why this happens
            pass
        except Exception as e:
            logging.error(traceback.format_exception(None, e, e.__traceback__))
        for receiver in receivers:
            headers = {
                'dataset': message.headers.get('dataset'),
                'sender_id': message.headers['receiver_id'],
                'pipeline_id': message.headers['pipeline_id'],
                'receiver_id': receiver['vertex']['id'],
            }
            out = aio_pika.Message(
                body=message.out,
                headers=headers,
                correlation_id=message.info()['correlation_id'])
            yield out, receiver['vertex']['func']
