import functools
import inspect
from typing import Any, Dict
import urllib

import asyncpg

from vertex import settings


def s3():
    s3_client = aioboto3.client("s3",
                                endpoint_url=settings.S3_ENDPOINT,
                                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                                config=botocore.client.Config(signature_version='s3v4'))
    return s3_client


class DB:
    def __init__(self, model: str):
        self.model = model

    async def request(self, method_name, path=None, params=None, data=None):
        method = getattr(requests, method_name)
        url = f'{settings.REST_URL}/{self.model}/{path}'
        res = await method(url, data=value)
        if 'application/json' in res.headers['Content-Type']:
            data = await res.json()
        else:
            data = await res.text()
        if res.status >= 400:
            logging.warn(f'{res.status} {method_name.upper()} {url}')
        return res.status, data
    
    def __getattr__(self, name):
        return functools.partial(self.request, name)
