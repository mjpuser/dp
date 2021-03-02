import json
import logging
import urllib
import uuid

import aio_pika

from vertex import service


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
        logging.info(f'S3 select on {bucket} {key}')
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
        event_stream = res['Payload']
        # Iterate over events in the event stream as they come
        async for event in event_stream:
            # If we received a records event, write the data to a file
            if 'Records' in event:
                data = event['Records']['Payload'].decode(
                    'utf-8').strip().split('\n')
                for datum in data:
                    message = aio_pika.Message(body=datum.encode('utf-8'))
                    yield datum.encode('utf-8'), f'{{name}}.{get_dataset_name(key)}'
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
    if status < 400:
        logging.info(f'Dataset {name} added successfully')
    elif status == 409:
        logging.info(f'Dataset {name} already added')
        return
    else:
        logging.error(f'Dataset {name} failed to add')
        return
    status, pipeline = await service.DB('vertex').get(params={'select': 'id,vertex(id,func,vertex_connection.sender(receiver(id,func)))',
                                                              'name': 'eq.dataset',
                                                              'vertex.func': 'eq.vertex.s3.register_dataset'},
                                                      headers={'accept': 'application/vnd.pgrst.object+json'})
    if status < 400:
        out = aio_pika.Message(body=message.body, headers={
            'correlation_id': str(uuid.uuid4()),
            'sender_id': pipeline['vertex']['id'],
            'pipeline_id': pipeline['id'],
            'receiver_id': pipeline['vertex']['vertex_connection']['receiver']['id']})
        yield out, pipeline['vertex']['vertex_connection']['receiver']['func']
    else:
        logging.error('Unable to find dataset pipeline')
        return


async def write(config, message):
    body = json.loads(message.body)
    async with service.s3() as s3:
        try:
            await s3.put_object(
                Body=json.dumps(body).encode('utf-8'),
                Bucket=config['bucket'],
                Key=config['key'].format(
                    message={**{'id': str(uuid.uuid4())}, **body}),
            )
        except Exception as e:
            logging.warn(f'Fix me {e}')
        yield None, None
