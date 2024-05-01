"""
Log production events
"""

import os
from . import logtail_handler, settings


LOGGER = logtail_handler.logger

def log_event(prelude_message=None, logs_context=None):
    if os.getenv("SCOPE") == "production":
        LOGGER.info(prelude_message, extra=logs_context)
    return True
