import logging

import urllib

from vertex import settings, service


async def split(config, message):
    event_name = message.get('EventName', '')
    if not event_name.startswith('s3:ObjectCreated'):
        logging.info(f'Skip processing event `{event_name}`.  Must be an s3:ObjectCreated* event')
        return

    bucket = message['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote(message['Records'][0]['s3']['object']['key'])
    content_type = message['Records'][0]['s3']['object']['contentType']

    if content_type != 'text/csv':
        logging.info(f'Skip processing file {bucket}/{key} since content type is {content_type}.  File must be a CSV to process')
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
                'CompressionType': 'NONE', #'NONE'|'GZIP'|'BZIP2',d
            },
            OutputSerialization={ 'JSON': {} },
        )
        event_stream = res['Payload']
        # Iterate over events in the event stream as they come
        async for event in event_stream:
            # If we received a records event, write the data to a file
            if 'Records' in event:
                data = event['Records']['Payload'].decode('utf-8').strip().split('\n')
                for datum in data:
                    yield datum.encode('utf-8'), '/'.join(key.split('/')[:-1])
            elif 'End' in event:
                end_event_received = True
        if not end_event_received:
            raise Exception("End event not received, request incomplete.")
        event_stream.close()


async def register_dataset(config, message):
    event_name = message.get('EventName', '')
    if not event_name.startswith('s3:ObjectCreated'):
        logging.info(f'Skip processing event `{event_name}`.  Must be an s3:ObjectCreated* event')
        return

    bucket = message['Records'][0]['s3']['bucket']['name']
    if bucket != config['bucket']:
        logging.info(f'Skip since bucket is not {config["bucket"]}')
        return

    key = urllib.parse.unquote(message['Records'][0]['s3']['object']['key'])
    name = key.split('/')[0]
    dataset = service.DB('dataset')
    status, message = await dataset.post(data={'name': name})
    if status < 400:
        logging.info(f'Dataset {name} added successfully')
    elif status == 409:
        logging.info(f'Dataset {name} already added')
    else:
        logging.error(f'Dataset {name} failed to add')
    yield None, None
