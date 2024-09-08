import logging

BASE_NAME = __name__

__all__ = ["log"]

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s|%(levelname)s|%(name)s|%(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S.000%z'
)

log = logging.getLogger(BASE_NAME)