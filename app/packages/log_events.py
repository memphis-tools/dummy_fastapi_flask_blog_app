"""
Log production events
"""

import os

try:
    import logtail_handler
except ModuleNotFoundError:
    from app.packages import logtail_handler

LOGGER = logtail_handler.logger


def log_event(prelude_message=None, logs_context=None):
    """
    Description:; used by the logger.

    paramaters:
    prelude_message -- str, main message which appears in betterstack
    logs_context -- dict, gives detail of the log sent
    """
    if os.getenv("SCOPE") == "production":
        LOGGER.info(prelude_message, extra=logs_context)
    return True
