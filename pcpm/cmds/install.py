import logging
import os
from pathlib import Path
import shutil
from types import ModuleType

from ..ds import Config, PKGS_MIRROR, PKGS_PATH, ROOT_PATH, InitFuncType, PackageConfig
from ..utils import download, untar, get_module, load_config, write_config, load_pkg_config

logger = logging.getLogger(__name__)


def download_pkg(p: str, config: Config) -> bool:
    flag: bool = False

    mirrors: list[str] = config.get("mirrors", []) + [PKGS_MIRROR]
    for m in mirrors:
        if m.startswith(("http", "https")):
            if download(f"{m}/{p}.tar.gz", f"{PKGS_PATH}/{p}.tar.gz"):
                flag = True
                break  
        else:
            try:
                shutil.copyfile(Path(m)/f"{p}.tar.gz", f"{PKGS_PATH}/{p}.tar.gz")
                flag = True
                break
            except:
                pass

    if not flag: 
        logger.error(f"ошибка при скачивание пакета: {p}")
        return False
    
    untar(f"{PKGS_PATH}/{p}.tar.gz", PKGS_PATH)
    os.remove(f"{PKGS_PATH}/{p}.tar.gz")

    return True

def init_pkg(p: str, config: Config) -> bool:
    pkg_config: PackageConfig|None = load_pkg_config(p)
    if not pkg_config is None:
        pkg_dependencies: dict|None = pkg_config["dependencies"] if "dependencies" in pkg_config else None
        if not pkg_dependencies is None:
            if not install_pkgs(pkg_dependencies.keys(), config, False):
                return False

    try:
        main_mod: ModuleType|None = get_module(p)
        if main_mod is None: raise Exception("main_mod is None")

        init_fn: InitFuncType = main_mod.init
        default_mod_conf = init_fn(ROOT_PATH, PKGS_PATH / p)
        if default_mod_conf is None: raise Exception("default_mod_conf is None")
        
        dependencies: dict|None = config["dependencies"] if "dependencies" in config else None
        if dependencies is None: 
            logger.error("dependencies is None")
            return False

        dependencies[p] = default_mod_conf
    except Exception as e:
        logger.error(f"Ошибка инициализации модуля {p} e: {e}")
        return False
    
    return True

def install_pkgs(pkgs: list[str], config: Config, forse: bool) -> bool:
    if len(pkgs) == 0: 
        pkgs += config["dependencies"].keys() if "dependencies" in config else []
    for p in pkgs:
        if not forse and p in config["dependencies"] and os.path.exists(PKGS_PATH/p):
            logger.info(f"{p} уже установлен")
            continue
        if not download_pkg(p, config) or not init_pkg(p, config):
            return False

    return True


def install(pkg_names: list[str], forse: bool):
    config: Config|None = load_config()
    if config is None: return

    os.makedirs(PKGS_PATH, exist_ok=True)

    if config.get("dependencies") is None: config['dependencies'] = {}

    if not install_pkgs(pkg_names, config, forse):
        return


    write_config(config)