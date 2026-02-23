import logging
import json
import os
from pathlib import Path

from ..ds import SRC_PATH, Config
from ..utils import get_bin_suffix, write_config, get_template_config

logger = logging.getLogger(__name__)


C_HELLO_WORLD = """#include <stdio.h>

int main(void){
    printf("Hello World!\\n");
    return 0;
}
"""

def init(name: str|None, dir: str|None):
    if name is None:
        name = input("Имя проекта: ")
        name = name.strip()
        if not name:
            logger.error("name не может быть пустым!")
            return
        
    if dir is None:
        dir = name

    project_dir = Path(".")/dir
    if os.path.exists(project_dir):
        logger.error(f"{project_dir} УЖЕ ЕСТЬ!")
        return

    os.makedirs(project_dir)
    os.makedirs(project_dir/SRC_PATH)

    with open(project_dir/SRC_PATH/"main.c", "+w") as fd:
        fd.write(C_HELLO_WORLD)

    
    # config = Config(name=name, target_name=name+get_bin_suffix())
    config = Config(name=name, target_name=name)
    template_config: Config|None = get_template_config()
    if template_config is not None:
        if "compilation_args" in template_config: config["compilation_args"] = template_config["compilation_args"]
        if "compiler" in template_config: config["compiler"] = template_config["compiler"]
        if "linker" in template_config: config["linker"] = template_config["linker"]
        if "linking_args" in template_config: config["linking_args"] = template_config["linking_args"]
        if "origin" in template_config: config["origin"] = template_config["origin"]
        if "workers" in template_config: config["workers"] = template_config["workers"]
        if "mirrors" in template_config: config["mirrors"] = template_config["mirrors"]
        
    write_config(config, project_dir/"config.json")