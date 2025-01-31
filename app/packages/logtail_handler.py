""" conf pour log sur betterstack"""
import os
import logging
from logtail import LogtailHandler

try:
    from utils import get_secret
except ModuleNotFoundError:
    from app.packages.utils import get_secret


if os.getenv("SCOPE") == "production":
    handler = LogtailHandler(source_token=f"{get_secret("/run/secrets/BETTERSTACK_SOURCE_TOKEN")}")
else:
    handler = LogtailHandler(source_token=f"{os.getenv("BETTERSTACK_SOURCE_TOKEN")}")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(handler)
