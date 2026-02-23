import os
import shutil
import logging
from types import ModuleType

from ..utils import load_config, write_config, get_module
from ..ds import Config, PKGS_PATH, RemoveFuncType, ROOT_PATH

logger = logging.getLogger(__name__)


def remove(pkgs: list[str]):
    config: Config|None = load_config()
    if config is None: return None
    
    for p in pkgs:
        if os.path.exists(PKGS_PATH/p): 
            
            try:
                main_mod: ModuleType|None = get_module(p)
                if main_mod is None: raise Exception("module is None")
                
                rm_fn: RemoveFuncType|None = main_mod.remove
                if rm_fn is None: return None

                conf: dict|None = config["dependencies"][p] if "dependencies" in config and p in config["dependencies"] else None
                rm_fn(ROOT_PATH, PKGS_PATH/p, conf)
            except Exception as e:
                logger.error(f"Ошибка удаления модуля (вызова remove) {p} e: {e}")

            shutil.rmtree(PKGS_PATH/p) 
        
        if "dependencies" in config and p in config["dependencies"]:
            del config["dependencies"][p]

    write_config(config)