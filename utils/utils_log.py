import logging
from typing import Union

logging.basicConfig(format='[%(levelname)s] %(asctime)s - %(message)s', level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


def log_info(msg: Union[str, int]):
    """Function to log information, call to this function ensures that the BasicConfig & logging level are respected"""
    logging.info(msg)
