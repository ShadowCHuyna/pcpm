import logging
import os
from pathlib import Path
import subprocess
import signal

from ..ds import BIN_PATH, Config
from ..utils import get_platform, load_config, get_bin_suffix

logger = logging.getLogger(__name__)

def run(args: list[str]):
    config: Config|None = load_config()
    if config is None: return
        

    if not os.path.exists(Path("./")/BIN_PATH/(config['target_name']+get_bin_suffix())):
        logger.error(f"'{BIN_PATH/config['target_name']}' не найден!")
        return
    
    proc = None
    try:
        proc = None
        if get_platform().startswith("windows"):
            proc = subprocess.Popen([str(BIN_PATH/(config['target_name']+get_bin_suffix()))] + args, cwd=BIN_PATH)
        else:
            proc = subprocess.Popen(["./"+config['target_name']+get_bin_suffix()] + args, cwd=BIN_PATH)
        proc.wait()
    except KeyboardInterrupt:
        if proc and proc.poll() is None: 
            proc.send_signal(signal.SIGINT)
            proc.wait()  
    except Exception as e:
        logger.error(f"Ошибка при запуске!\n{e}")
    logger.info("завершение")