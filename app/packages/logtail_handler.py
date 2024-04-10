""" conf pour log sur betterstack"""
import os
import logging
from logtail import LogtailHandler


handler = LogtailHandler(source_token=f"{os.getenv('BETTERSTACK_SOURCE_TOKEN')}")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(handler)
