import json
import logging
import sys
from logging import Formatter
from pathlib import Path


class JsonFormatter(Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record):
        return json.dumps(record)


def init_logging(logger_name: str, log_path: str = "logs/info.log") -> logging.Logger:
    """_summary_

    Parameters
    ----------
    logger_name : str
        _description_
    log_path : str, optional
        _description_, by default "logs/info.log"

    Returns
    -------
    logging.Logger
        _description_
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    path = Path(log_path)

    dir_path = path.parent
    if not dir_path.exists():
        dir_path.mkdir(parents=True)

    if logger.handlers == []:
        dir_path.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "log": %(message)s}'
        )

        # file handler
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        # console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        logger.propagate = False

    return logger
