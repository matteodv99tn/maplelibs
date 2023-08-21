import json
import shutil
import os
import subprocess

from os.path import dirname, join
from glob import glob

autobuild: bool = False

args = os.sys.argv
if "build" in args:
    autobuild = True
    args.remove("build")

if len(args) < 2:
    print("Usage: python generate.py <json_files> <target_dir> [build (opt)]")
    exit(1)


target_dir = args[-1]
sources = args[1:-1]

if target_dir is None:
    BASE_DIR = join(os.getcwd(), "maple_codegen")
else:
    BASE_DIR = target_dir

INCLUDE_DIR = join(BASE_DIR, "include", "maple_codegen")
SRC_DIR = join(BASE_DIR, "src")
WRAP_DIR = join(BASE_DIR, "pythonwraps")
TEMPLATE_DIR = join(dirname(__file__), "templates")

os.makedirs(INCLUDE_DIR, exist_ok=True)
os.makedirs(SRC_DIR, exist_ok=True)
os.makedirs(WRAP_DIR, exist_ok=True)


def format_code(path):
    if shutil.which("clang-format") is not None:
        try:
            subprocess.run(["clang-format", "-i", path], check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to format {path} with clang-format")


def process_codegen_input(json_filename: str):
    with open(json_filename, "r") as file:
        generated_data = json.load(file)

    name = generated_data["name"].lower()

    signature = list()
    initialization = list()

    if generated_data["has_x"]:
        signature.append("VectorRef x")
        # signature.append("const Vector& x")
        for idx, state in enumerate(generated_data["x"]):
            initialization.append(f"const float_t {state} = x[{idx}];")

    if generated_data["has_u"]:
        signature.append("VectorRef u")
        # signature.append("const Vector& u")
        for idx, input in enumerate(generated_data["u"]):
            initialization.append(f"const float_t {input} = u[{idx}];")

    signature = ", ".join(signature)
    initialization = "\n".join(initialization)

    source_file_name = f"{name}.cpp"
    header_file_name = f"{name}.hpp"
    params_file_name = f"{name}_params.hpp"
    wrapper_file_name = f"{name}_wrapper.cpp"
    module_name = name.lower()

    code_subs = {"INCLUDE": name.upper(),
                 "modulename": module_name,
                 "headername": name.lower(),
                 "declarations": "",
                 "implementations": "",
                 "parameters": "",
                 "wrap_defs": ""}

    # --- Parameters
    pars = generated_data["p"]
    pars_vals = generated_data["p_values"]
    for (p_name, p_value) in zip(pars, pars_vals):
        code_subs["parameters"] += f"#define {p_name} {p_value}\n"

    # --- Function
    fun_name = f"{name}"
    decl = f"Vector {fun_name}({signature})"
    code_subs["declarations"] += decl + ";\n"
    code_subs["implementations"] += decl + f""" {{
        {initialization}

        {generated_data["func"]}
        return func;
        }}\n\n\n
        """
    code_subs["wrap_defs"] += f"m.def(\"{fun_name}\", &{fun_name});\n"

    # --- Function jacobian dx
    if generated_data["has_x"]:
        fun_name = f"{name}_dx"
        decl = f"Matrix {fun_name}({signature})"
        code_subs["declarations"] += decl + ";\n"
        code_subs["implementations"] += decl + f""" {{
            {initialization}

            {generated_data["func_dx"]}
            return func_dx;
            }}\n\n\n
            """
        code_subs["wrap_defs"] += f"m.def(\"{fun_name}\", &{fun_name});\n"

    # --- Function jacobian du
    if generated_data["has_u"]:
        fun_name = f"{name}_du"
        decl = f"Matrix {fun_name}({signature})"
        code_subs["declarations"] += decl + ";\n"
        code_subs["implementations"] += decl + f""" {{
            {initialization}

            {generated_data["func_du"]}
            return func_du;
            }}\n\n\n
            """
        code_subs["wrap_defs"] += f"m.def(\"{fun_name}\", &{fun_name});\n"

    with open(join(TEMPLATE_DIR, "file.hpp"), "r") as base_file:
        content = base_file.read()
        for key, value in code_subs.items():
            content = content.replace(f"${key}", value)

        out_file_name = join(INCLUDE_DIR, header_file_name)
        with open(out_file_name, "w") as out_file:
            out_file.write(content)
        format_code(out_file_name)

    with open(join(TEMPLATE_DIR, "file_params.hpp"), "r") as base_file:
        content = base_file.read()
        for key, value in code_subs.items():
            content = content.replace(f"${key}", value)

        out_file_name = join(INCLUDE_DIR, params_file_name)
        with open(out_file_name, "w") as out_file:
            out_file.write(content)
        format_code(out_file_name)

    with open(join(TEMPLATE_DIR, "file.cpp"), "r") as base_file:
        content = base_file.read()
        for key, value in code_subs.items():
            content = content.replace(f"${key}", value)

        out_file_name = join(SRC_DIR, source_file_name)
        with open(out_file_name, "w") as out_file:
            out_file.write(content)
        format_code(out_file_name)

    with open(join(TEMPLATE_DIR, "wrapper.cpp"), "r") as base_file:
        content = base_file.read()
        for key, value in code_subs.items():
            content = content.replace(f"${key}", value)

        out_file_name = join(WRAP_DIR, wrapper_file_name)
        with open(out_file_name, "w") as out_file:
            out_file.write(content)
        format_code(out_file_name)


if __name__ == "__main__":

    print("--> Maple code generation, output directory:", target_dir)
    for source in sources:
        print("--> Processing", source)
        process_codegen_input(source)

    print("--> Generating CMakeLists.txt")
    with open(join(WRAP_DIR, "CMakeLists.txt"), "w") as out_file:
        files = glob(join(WRAP_DIR, "*_wrapper.cpp"))
        files = [os.path.split(f)[-1] for f in files]

        for f in files:
            wrap = f"${{WRAPPER_FILE_DIR}}/{f}"
            src = f"${{SOURCE_FILE_DIR}}/{f.replace('_wrapper', '')}"
            module_name = f.replace("_wrapper.cpp", "")
            out_file.write(f"pybind11_add_module({module_name} \n"
                           f"    {wrap}\n"
                           f"    {src}\n"
                           f"    )\n")
        out_file.write("\n\n")
        for f in files:
            module_name = f.replace("_wrapper.cpp", "")
            out_file.write(f"install(TARGETS {module_name} "
                           "DESTINATION ${MODULE_INSTALL_DIR})\n")

    # copy mapledefines.hpp
    shutil.copy(join(TEMPLATE_DIR, "mapledefines.hpp"),
                join(INCLUDE_DIR, "mapledefines.hpp"))
    # copy CMakeLists.txt
    shutil.copy(join(TEMPLATE_DIR, "CMakeLists.txt"),
                join(BASE_DIR, "CMakeLists.txt"))

    if autobuild:
        from multiprocessing import cpu_count

        print("--> Building")
        build_dir = join(BASE_DIR, "build")
        os.makedirs(build_dir, exist_ok=True)
        os.chdir(build_dir)
        subprocess.run(["cmake", ".."], check=True)
        subprocess.run(["make", f"-j{cpu_count()}"], check=True)
        subprocess.run(["make", "install"], check=True)
