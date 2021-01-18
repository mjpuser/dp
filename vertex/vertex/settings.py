# -*- coding: utf-8 -*-

from decouple import config


RABBITMQ_HOST: str = config('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER: str = config('RABBITMQ_USER', 'admin')
RABBITMQ_PASS: str = config('RABBITMQ_PASS', 'admin')

REST_URL: str = config('REST_URL', 'http://rest:3000')
