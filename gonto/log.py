"""Gonto logging."""

import os
import logging

from . import APPLICATION_SHORT_ID

#: Defines whether debugging is enabled or not.
DEBUG: bool = "GONTO_DEBUG" in os.environ

logging.basicConfig(
    format="[%(levelname)7s] (%(name)s) %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO,
)

#: Logger object.
#:
#: ::
#:
#:    logger.debug("Debug message")
#:    logger.info("Info message")
#:    logger.warning("Warning message")
#:    logger.error("Error message")
#:
#: See: https://docs.python.org/3/library/logging.html#logger-objects
logger: logging.Logger = logging.getLogger(APPLICATION_SHORT_ID)
