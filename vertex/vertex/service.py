import functools
import logging
import typing
from typing import Optional, Tuple, Union

import aioboto3
from aiohttp_requests import requests
import botocore.client

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

    async def request(self, method_name: str, path: str = '', params: Optional[dict] = None, data: Optional[dict] = None, headers: Optional[dict] = None) -> Tuple[int, Optional[dict]]:
        method = getattr(requests, method_name)
        url = f'{settings.REST_URL}/{self.model}{path}'
        res = await method(url, data=data, params=params, headers=headers)
        ct = res.headers.get('Content-Type', '')
        if 'application/json' in ct or 'application/vnd.pgrst.object+json' in ct:
            data = await res.json()
        else:
            data = await res.text()
        if res.status >= 400:
            logging.warn(f'{res.status} {method_name.upper()} {url}')
        return typing.cast(int, res.status), data

    def __getattr__(self, name):
        return functools.partial(self.request, name)
