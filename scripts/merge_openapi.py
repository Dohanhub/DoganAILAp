#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Dict, Any, List

try:
    import httpx  # type: ignore
except Exception:
    httpx = None  # Fallback to urllib
import urllib.request


def fetch_spec(source: str) -> Dict[str, Any]:
    if source.startswith("http://") or source.startswith("https://"):
        if httpx:
            r = httpx.get(source, timeout=15)
            r.raise_for_status()
            return r.json()
        with urllib.request.urlopen(source, timeout=15) as resp:  # nosec - controlled input
            return json.loads(resp.read().decode("utf-8"))
    with open(source, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_specs(specs: List[Dict[str, Any]]) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "openapi": "3.0.3",
        "info": {"title": "DoganAI Combined API", "version": "1.0.0"},
        "paths": {},
        "components": {"schemas": {}, "securitySchemes": {}},
        "tags": [],
    }
    tags_seen = set()

    for spec in specs:
        # merge paths
        for path, item in spec.get("paths", {}).items():
            if path not in base["paths"]:
                base["paths"][path] = item
            else:
                # merge methods
                base["paths"][path].update(item)

        # merge components/schemas
        comps = spec.get("components", {})
        for section in ("schemas", "parameters", "responses", "securitySchemes"):
            if section in comps:
                base["components"].setdefault(section, {})
                for k, v in comps[section].items():
                    if k not in base["components"][section]:
                        base["components"][section][k] = v

        # merge tags
        for t in spec.get("tags", []) or []:
            name = t.get("name")
            if name and name not in tags_seen:
                base["tags"].append(t)
                tags_seen.add(name)

    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--services", help="comma-separated list of OpenAPI JSON URLs or files", required=True)
    ap.add_argument("--out", help="output JSON file", required=True)
    args = ap.parse_args()

    sources = [s.strip() for s in args.services.split(",") if s.strip()]
    specs = []
    for s in sources:
        try:
            specs.append(fetch_spec(s))
        except Exception as e:
            print(f"WARN: failed to load {s}: {e}", file=sys.stderr)

    if not specs:
        raise SystemExit("no specs loaded; aborting")

    combined = merge_specs(specs)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)
    print(f"Wrote combined OpenAPI to {args.out}")


if __name__ == "__main__":
    main()
