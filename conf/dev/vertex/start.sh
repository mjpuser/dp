#!/usr/bin/env bash

set -e

pipenv install
pipenv shell python main.py
