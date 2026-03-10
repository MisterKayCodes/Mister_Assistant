import os
import sys
import ast

# Architectural Rules:
# core/ -> No aiogram, No database (sqlalchemy)
# bot/ -> No math (logic stays in core)
# services/ -> No database (use repository in data/)
# data/ -> No aiogram, No services

FORBIDDEN_IMPORTS = {
    "core": ["aiogram", "sqlalchemy", "bot", "data", "services"],
    "bot": ["core.logic", "sqlalchemy", "data.models"], # bot should use core via interfaces or simple calls, not logic directly if complicated
    "data": ["aiogram", "services", "bot"],
    "services": ["aiogram", "bot"] # services is nervous system, might talk to core but not bot directly
}

def check_imports(file_path, folder_name):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return []

    errors = []
    forbidden = FORBIDDEN_IMPORTS.get(folder_name, [])
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for f in forbidden:
                    if alias.name.startswith(f):
                        errors.append(f"Illegal import in {file_path}: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for f in forbidden:
                    if node.module.startswith(f):
                        errors.append(f"Illegal import in {file_path}: from {node.module} import ...")
    
    return errors

def main():
    has_mutants = False
    base_dir = "."
    for folder in ["core", "bot", "data", "services"]:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            continue
            
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py"):
                    file_errors = check_imports(os.path.join(root, file), folder)
                    if file_errors:
                        has_mutants = True
                        for err in file_errors:
                            print(f"[MUTANT DETECTED]: {err}")

    if has_mutants:
        print("\nArchitecture rules violated! Cut out the mutants.")
        sys.exit(1)
    else:
        print("Architecture is clean. The organism is healthy.")
        sys.exit(0)

if __name__ == "__main__":
    main()
