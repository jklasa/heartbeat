import logging
import os

if "LOG_LEVEL" in os.environ:
    level = logging.getLevelName(os.environ["LOG_LEVEL"])
else:
    level = logging.INFO

log = logging
log.basicConfig(
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=level,
)
