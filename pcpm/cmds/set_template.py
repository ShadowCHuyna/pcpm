from pathlib import Path
import logging

from ..ds import Config
from ..utils import load_config, write_config, get_config_dir

logger = logging.getLogger(__name__)


def set_template():
    config: Config|None = load_config()
    if config is None: return

    config_dir: Path|None = get_config_dir()
    if config_dir is None: return

    write_config(config, config_dir/"config.json")
    logger.info(f"создан template в: {config_dir/"config.json"}")
    