import os
import sys
import glob
import json

def check_no_placeholders():
    for root, dirs, files in os.walk("engine/modules"):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    content = f.read()
                    if "PLACEHOLDER" in content or "demo" in content.lower():
                        print(f"Placeholder code found in {file}")
                        sys.exit(1)

def check_module_manifests():
    modules = glob.glob("engine/modules/*/")
    for module in modules:
        manifest = os.path.join(module, "module.json")
        if not os.path.exists(manifest):
            print(f"Missing manifest for module {module}")
            sys.exit(1)
        with open(manifest, encoding="utf-8") as f:
            data = json.load(f)
            if not all(k in data for k in ("name", "version", "interfaces", "dependencies")):
                print(f"Incomplete manifest in {manifest}")
                sys.exit(1)

if __name__ == "__main__":
    check_no_placeholders()
    check_module_manifests()
    print("Engine contract checks passed.")
