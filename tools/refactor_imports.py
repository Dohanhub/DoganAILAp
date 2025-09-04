import pathlib, sys, ast, astunparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

# Map old module names to new dotted paths (extend freely)
MAP = {
    "database": "core.database",
    "validators": "utils.validators",
    "monitoring": "services.monitoring",
    "compliance": "services.compliance",
    "shard_router": "core.shard_router",
    "cli": "core.cli",  # or "cli" if you split it
    "engine_connection_report": "core.engine_connection_report",
    "regulatory_auth_manager": "core.regulatory_auth_manager",
    "regulatory_web_scraper": "ingest.regulatory_web_scraper",
    "website_auto_connector": "ingest.website_auto_connector",
    "simple_evaluation": "eval.simple_evaluation",
    # add the rest as you finalize moves
}

def rewrite(tree: ast.AST) -> bool:
    changed = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in MAP:
                    alias.name = MAP[alias.name]
                    changed = True
        elif isinstance(node, ast.ImportFrom):
            if node.module in MAP:
                node.module = MAP[node.module]
                changed = True
    return changed

def files_to_touch():
    for p in ROOT.rglob("*.py"):
        # skip virtual envs, build dirs, and this script
        if any(seg in {".venv", "venv", "build", "dist", ".git"} for seg in p.parts):
            continue
        if p.name == "refactor_imports.py":
            continue
        yield p

def main():
    n_changed = 0
    for path in files_to_touch():
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except Exception:
            continue
        if rewrite(tree):
            new_src = astunparse.unparse(tree)
            path.write_text(new_src, encoding="utf-8")
            n_changed += 1
    print(f"Rewritten files: {n_changed}")

if __name__ == "__main__":
    try:
        import astunparse  # pip install astunparse
    except ImportError:
        print("Please: pip install astunparse")
        sys.exit(1)
    main()