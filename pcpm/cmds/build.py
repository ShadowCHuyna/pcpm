import logging
import os
from pathlib import Path
import subprocess
import shutil

from ..ds import BIN_PATH, TMP_SRC_PATH, COMPILE_ARGS, Config, BuildArgs, BUILD_PATHS, PKGS_PATH, BuildFuncType, TMP_SRC_PATH, SRC_PATH, OBJS_PATH
from ..utils import get_compiler, get_module, load_config, get_linker, compile

logger = logging.getLogger(__name__)

def make_build_folder():
    if TMP_SRC_PATH.exists():
        shutil.rmtree(TMP_SRC_PATH)
        
    for dir in BUILD_PATHS:
        os.makedirs(dir, exist_ok=True) 
    
def build_pkgs(config: Config) -> BuildArgs|None:
    all_ba: BuildArgs = {"link":[],"objs":[],"source":[]}
    
    dependencies: dict|None = config["dependencies"] if "dependencies" in config else None
    if dependencies is None: 
        logger.error("dependencies is None")
        return None

    for p in dependencies.keys():
        try:
            main_mod = get_module(p)
            if main_mod is None: return None
            build_fn: BuildFuncType = main_mod.build
            ba: BuildArgs|None = build_fn(TMP_SRC_PATH, PKGS_PATH/p, dependencies[p])
            if ba is None: raise Exception("BuildArgs is None")
        except Exception as e:
            logger.error(f"Ошибка сборки модуля {p} e: {e}")
            return None

        all_ba["link"] += ba["link"]
        all_ba["source"] += ba["source"]
        all_ba["objs"] += ba["objs"]

    
    return all_ba

def build_src(source_args: list[str]) -> list[str] | None:
    config: Config | None = load_config()
    if config is None:
        return None
    src_s = list(TMP_SRC_PATH.rglob("*.c"))
    dst_s: list[Path] = []

    compilation_args: list[str] = (
        config["compilation_args"]
        if "compilation_args" in config
        else COMPILE_ARGS
    )

    for src in src_s:
        rel_path: Path = src.relative_to(TMP_SRC_PATH)
        obj_file: Path = OBJS_PATH / rel_path.with_suffix(".o")
        obj_file.parent.mkdir(parents=True, exist_ok=True)
        dst_s.append(obj_file)

    return compile(src_s, dst_s, compilation_args+source_args)

def build_assets(assets: list[str]):
    for asset in assets:
        src = Path(asset).resolve()

        if not src.exists():
            raise FileNotFoundError(f"Asset not found: {src}")

        dst = BIN_PATH / src.name

        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            if dst.exists():
                os.remove(dst)
                 
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

def build() -> bool:
    make_build_folder()

    config: Config|None = load_config()
    if config is None: return False
    
    shutil.copytree(SRC_PATH, TMP_SRC_PATH, dirs_exist_ok=True)

    build_args: BuildArgs = {"link":[],"objs":[],"source":[]}

    if not (config.get("dependencies") is None):
        ba = build_pkgs(config)
        if ba is None: return False
        build_args["link"] += ba["link"]
        build_args["source"] += ba["source"]
        build_args["objs"] += ba["objs"]

    obj_files = build_src(build_args["source"])
    if obj_files is None: return False
    build_args["objs"] += obj_files

    logger.info("ЛИНКУЕМ ВСЕ!!!")
    ln: str|None = get_linker()
    if ln is None: return False

    cmd: list[str] = [ln, "-o", str(BIN_PATH/config['target_name'])]
    cmd += build_args["objs"]
    cmd += build_args["source"]
    cmd += build_args["link"]
    cmd += config["linking_args"] if "linking_args" in config else [] 
    cmd += ["-Wl,-rpath,$ORIGIN/"+config["origin"]] if "origin" in config else []

    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        logger.error(f"Ошибка линковки!")
        logger.info(cmd)
        return False

    if "assets" in config: build_assets(config["assets"])

    logger.info("Работа сделана!")
    return True