import os
import sys
import ast
import argparse

# Architectural Rules:
# core/ -> No aiogram, No database (sqlalchemy)
# bot/ -> No core.logic (direct logic), No database (sqlalchemy)
# services/ -> No bot, No database (sqlalchemy)
# data/ -> No aiogram, No services, No bot

DEFAULT_FORBIDDEN_IMPORTS = {
    "core": ["aiogram", "sqlalchemy", "bot", "data", "services"],
    "bot": ["sqlalchemy", "data.models"], 
    "data": ["aiogram", "services", "bot"],
    "services": ["aiogram", "bot", "sqlalchemy"]
}

def check_file_integrity(file_path, folder_name, forbidden_rules, max_lines=200):
    errors = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) > max_lines:
            errors.append(f"File too long ({len(lines)} lines > {max_lines}). Refactor into smaller components.")
        
        content = "".join(lines)
        try:
            tree = ast.parse(content)
        except Exception as e:
            return [f"Syntax Error in {file_path}: {e}"]

    forbidden = forbidden_rules.get(folder_name, [])
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            else:
                if node.module:
                    names = [node.module]
            
            for name in names:
                for f in forbidden:
                    if name.startswith(f):
                        errors.append(f"Illegal import: {name}")
    
    return errors

def scan_organism(base_dir=".", max_lines=200):
    has_issues = False
    layers = list(DEFAULT_FORBIDDEN_IMPORTS.keys())
    
    print(f"[SCAN] Scanning Organism at '{base_dir}'...")
    
    for layer in layers:
        layer_path = os.path.join(base_dir, layer)
        if not os.path.exists(layer_path):
            continue
            
        for root, _, files in os.walk(layer_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    file_errors = check_file_integrity(full_path, layer, DEFAULT_FORBIDDEN_IMPORTS, max_lines)
                    if file_errors:
                        has_issues = True
                        for err in file_errors:
                            print(f"[!] [ISSUE] {full_path}: {err}")

    if has_issues:
        print("\n[X] Architecture is INFECTED. Follow the prompt.md and cut out the mutants.")
        return False
    else:
        print("[+] Organism is HEALTHY. All layers are pure.")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mister Assistant Architecture Inspector")
    parser.add_argument("--path", default=".", help="Root path of the project")
    parser.add_argument("--max-lines", type=int, default=200, help="Max lines allowed per file")
    args = parser.parse_args()
    
    if not scan_organism(args.path, args.max_lines):
        sys.exit(1)
    sys.exit(0)
