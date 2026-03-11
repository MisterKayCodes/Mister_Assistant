import os
import ast
import re
import sys

# The directories to scan and build an index from
SEARCH_DIRS = ["core", "services", "data", "bot", "utils"]

def build_project_index(base_path=".") -> dict:
    """
    Scans the codebase and returns a dictionary mapping:
    {'ClassName': 'module.path', 'function_name': 'module.path'}
    """
    index = {}
    print("[SCAN] Code Healer is building an index of the organism...")
    
    for directory in SEARCH_DIRS:
        layer_path = os.path.join(base_path, directory)
        if not os.path.exists(layer_path):
            continue
            
        for root, _, files in os.walk(layer_path):
            for file in files:
                if not file.endswith(".py"):
                    continue
                
                # Exclude this script and other automation scripts from being indexed as sources
                if root.startswith(os.path.join(base_path, "scripts")):
                    continue

                full_path = os.path.join(root, file)
                
                # Convert file path to module path (e.g., 'core\\nlu\\classifier.py' -> 'core.nlu.classifier')
                rel_path = os.path.relpath(full_path, base_path)
                module_path = rel_path.replace(os.sep, ".")[:-3]
                if module_path.endswith(".__init__"):
                    module_path = module_path[:-9]  # Remove .__init__
                
                with open(full_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=full_path)
                    except SyntaxError:
                        continue
                        
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        # Do not index private functions/classes
                        if not node.name.startswith("_"):
                            index[node.name] = module_path
                            
    return index

def heal_file(file_path: str, index: dict) -> bool:
    """
    Parses a single file's AST looking for broken imports.
    If it finds an import for a name that exists in our index BUT the
    current import path doesn't match the index's path, it rewrites the file.
    Returns True if the file was modified.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
    
    try:
        tree = ast.parse(file_content, filename=file_path)
    except SyntaxError:
        return False

    healed = False
    new_content = file_content
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
                
            for alias in node.names:
                imported_name = alias.name
                
                # Check if we know about this name locally
                if imported_name in index:
                    correct_module = index[imported_name]
                    current_module = node.module
                    
                    if current_module != correct_module:
                        print(f"[!] Healing anomaly in {file_path}")
                        print(f"    -> Redirecting '{imported_name}' from '{current_module}' to '{correct_module}'")
                        
                        # Use regex to safely find and replace the exact import line
                        # Match: from <current_module> import ...<imported_name>...
                        pattern = rf"(from\s+{re.escape(current_module)}\s+import\s+.*?\b){re.escape(imported_name)}(\b.*?)"
                        
                        # We need to extract it entirely. 
                        # Actually, it's safer to just replace the module path if the line is simple.
                        # For robustness, we will find the exact phrase `from X import` and replace it
                        # but what if there are multiple imports on one line? `from X import A, B`
                        # If B is right and A is wrong, changing X breaks B.
                        
                        # Safe Heuristic: Replace the entire module IF we are sure it moved.
                        # For now, let's keep it simple: If the file has `from Old.Path import Name`, 
                        # change `from Old.Path` to `from New.Path` ONLY ON THAT LINE.
                        
                        # Let's find the exact line in the file content based on lineno
                        lines = new_content.split('\n')
                        target_line = lines[node.lineno - 1]
                        
                        if current_module in target_line and imported_name in target_line:
                            if "," not in target_line or target_line.strip().startswith(f"from {current_module} import {imported_name}"):
                                # Safe to replace just the module string on this specific line
                                lines[node.lineno - 1] = target_line.replace(f"from {current_module}", f"from {correct_module}")
                                new_content = '\n'.join(lines)
                                healed = True
                            else:
                                print(f"    [!] Complex multi-import detected on line {node.lineno}. Splitting is advanced. Healer skipped for safety.")

    if healed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

def run_healer(base_path="."):
    index = build_project_index(base_path)
    print(f"[+] Index built. Found {len(index)} entities.")
    
    healed_count = 0
    
    print("[SCAN] Scanning for imported anomalies...")
    for directory in SEARCH_DIRS + ["tests", "scripts"]:
        layer_path = os.path.join(base_path, directory)
        if not os.path.exists(layer_path):
            continue
            
        for root, _, files in os.walk(layer_path):
            for file in files:
                if not file.endswith(".py") or file == "code_healer.py":
                    continue
                full_path = os.path.join(root, file)
                if heal_file(full_path, index):
                    healed_count += 1
                    
    if healed_count > 0:
        print(f"[+] Healer successfully corrected {healed_count} files.")
        return True
    else:
        print("[+] Codebase structure is syntactically sound.")
        return False

if __name__ == "__main__":
    run_healer()
