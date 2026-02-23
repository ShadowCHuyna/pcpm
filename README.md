# pcpm
A package manager for C in Python. Downloads libraries and generates code.

[ru readme](https://github.com/ShadowCHuyna/pcpm/blob/main/RU_README.md)

It was evening, there was nothing to do, and I thought: why not make a "package" manager for `C` libraries.
> In `C` there are no packages because there is no namespace mechanism. Everything lives in the global symbol space, so it’s more accurate to talk not about packages, but about a library manager.

Just downloading libraries is boring. Therefore, a package is a `python` script that can do some useful (or not so useful) stuff: generate code, prepare wrappers, pull binaries, anything.

---
## Table of Contents
* [Why](#why)
* [Examples](#examples)
  * [pjim](#pjim)
  * [raylib-module](#raylib-module)
* [Installation](#installation)
* [Commands](#commands)
* [Project Configuration](#project-configuration)
---
## Why?
I wanted:
1. dependency management.
2. to minimize manual setting of flags and paths.
3. code generation.
---
## Examples
### pjim
The `pjim` package generates 2 functions of the form
`pjim_<struct name>_<serialization/deserialization>`
for structures marked with `// @PJIM`.

Uses the library [tsoding/jim](https://github.com/tsoding/jim).
```c
#include <stdio.h>
#include "jim.h"
#include "jimp.h"
#include "pjim.h"

// @PJIM
typedef struct
{
    int number;
    int number_arr_capacity;
    int number_arr[10];
} some_struct;


int main(void){
    Jim jim = {.pp=4};
    some_struct ss = {.number=33, .number_arr_capacity=3};
    for (size_t i = 0; i < ss.number_arr_capacity; i++)
        ss.number_arr[i] = i;
    
    // serialization
    pjim_some_struct_serialization(&jim, &ss); // auto-generated function
    printf("serialized structure JSON:\n");
    fwrite(jim.sink, jim.sink_count, 1, stdout);

    // deserialization
    printf("\ndeserialized structure:\n");
    some_struct ds = {0};
    Jimp jimp = {0};
    jimp_begin(&jimp, "", jim.sink, jim.sink_count); 
    pjim_some_struct_deserialization(&jimp, &ds); // auto-generated function

    printf("{\n\t\"number\": %d,\n\t\"number_arr_capacity\": %d,\n\t\"number_arr\": [\n", ds.number, ds.number_arr_capacity);
    for (size_t i = 0; i < ds.number_arr_capacity; i++)
        printf("\t\t%d,\n", ds.number_arr[i]);
    printf("\t]\n}\n");
    return 0;
}
```
`./build/bin/main`:
```json
serialized structure JSON:
{
    "number": 33,
    "number_arr_capacity": 3,
    "number_arr": [
        0,
        1,
        2
    ]
}
deserialized structure:
{
    "number": 33,
    "number_arr_capacity": 3,
    "number_arr": [
        0,
        1,
        2,
    ]
}
```

So you just mark the structure, and the package generates the serialization/deserialization functions automatically.

To run the example:

1. `pcpm init`
2. `pcpm install pjim`
3. ctrl+c, ctrl+v
4. `pcpm build run`

---

### raylib-module
The `raylib-module` package is an attempt to make something like "modules."
If you try to link in a project two libraries that have at least one function with the same name (or you already have one), you get a linker error. Surprise.

Instead:
- `RaylibModule` - a structure with pointers to all functions.
- `import_RaylibModule` - loads the `dll/so` and fills the structure.
- In code, you work through `rl->FunctionName`.

There are no symbol conflicts because nothing is linked directly. Functions are loaded at runtime and stored in the pointer structure, not in the final binary’s symbol table.
Downside: macros tied to functions break. But they can be rewritten to use pointers.

Uses the library: [raysan5/raylib](https://github.com/raysan5/raylib)
```c
#include "raylib-module.h"
RaylibModule* rl;

int main(void){
    rl = import_RaylibModule("./libraylib.so.5.5.0");

    rl->InitWindow(800, 450, "raylib [core] example - basic window");
    while (!rl->WindowShouldClose())
    {
        rl->BeginDrawing();
            rl->ClearBackground(RAYWHITE);
            rl->DrawText("Congrats! You created your first window!", 190, 200, 20, LIGHTGRAY);
        rl->EndDrawing();
    }
    rl->CloseWindow();

    return 0;
}
```

To run:

1. `pcpm init`
2. `pcpm install raylib-module`
3. ctrl+c, ctrl+v
4. `pcpm build run`

---

## Installation
Dependencies:
- make
- python3
- pip
- git

Installation:
1. `git clone https://github.com/ShadowCHuyna/pcpm --depth=1`
2. `make install`

Uninstall: `make uninstall`

Project creation:
1. `pcpm init` - create a project
2. `pcpm build run` - build and run.
---
## Commands
```
init              Create a new project
install (i)       Install project dependencies
build (b)         Build the project
run (r)           Run the project
remove            Remove packages from the project
set_template      Create or update config.json template
```
---
## Project Configuration
```json
{
    "name": "example_name",
    "target_name": "example_bin_name",
    "mirrors": [
        "http://pcpmirror.potatom.ru/packages",
        "/example/path"
    ],
    "origin": "./libs",
    "compilation_args": ["-Wall", "-Wextra"],
    "compiler": "gcc",
    "linking_args": [],
    "linker": "ld",
    "workers": 4,
    "assets": [],
    "dependencies": {
        "pjim": {}
    }
}
```
* `name` - project name. Used inside `pcpm`, purely an identifier.
* `target_name` - final binary name.
* `mirrors` - list of package sources. Can be an HTTP mirror or a local directory.
* `origin` - where libraries are installed (default `./`).
* `compilation_args` - compiler flags (`-Wall`, `-O2`, etc.).
* `compiler` - which compiler to use (`gcc`, `clang`, etc.).
* `linking_args` - linker flags (`-lm`, `-lpthread`, etc.).
* `linker` - which linker to use.
* `workers` - number of build threads.
* `assets` - directories with resources (copied to `./build/bin`).
* `dependencies` - project dependencies.

`dependencies`, `assets`, `workers`, `linking_args`, `compiler`, `compilation_args`, `origin`, `mirrors` - optional.
