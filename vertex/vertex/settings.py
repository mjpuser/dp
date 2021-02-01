# -*- coding: utf-8 -*-

from decouple import config


RABBITMQ_HOST: str = config('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER: str = config('RABBITMQ_USER', 'admin')
RABBITMQ_PASS: str = config('RABBITMQ_PASS', 'admin')

REST_URL: str = config('REST_URL', 'http://rest:3000')

S3_ENDPOINT: str = config('S3_ENDPOINT', 'http://s3:9000')
S3_ACCESS_KEY_ID: str = config('S3_ACCESS_KEY_ID', 'minio')
S3_SECRET_ACCESS_KEY: str = config('S3_SECRET_ACCESS_KEY', 'minio678')
