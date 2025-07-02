"""
logger.logger
"""
import logging
import logging.config
from pathlib import Path
from ruamel.yaml import YAML


logging.config.dictConfig(
    YAML(typ='safe', pure=True).load(
        (
            Path(__file__) /
            '..' /
            'logger.cfg.yml'
        ).resolve()
    )
)


def get_logger(_name=None):
    """
    Return a configured logger.
    Args:
        _name (str): The module name.
    Returns:
        The logger instance.
    """
    return logging.getLogger(_name)
