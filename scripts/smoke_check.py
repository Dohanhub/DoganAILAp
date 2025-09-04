"""
Simple smoke test for DoganAI stack: API and Web.

Usage: python scripts/smoke_check.py [--api http://localhost:8010] [--web http://localhost:3001]
"""
import argparse
import sys
import time
import requests


def check_url(name: str, url: str, expect_status: int = 200, timeout: float = 5.0) -> bool:
    try:
        r = requests.get(url, timeout=timeout)
        ok = r.status_code == expect_status
        print(f"{name}: {url} -> {r.status_code} {'OK' if ok else 'FAIL'}")
        return ok
    except Exception as e:
        print(f"{name}: {url} -> ERROR: {e}")
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--api', default='http://localhost:8010')
    p.add_argument('--web', default='http://localhost:3001')
    args = p.parse_args()

    ok = True
    ok &= check_url('API health', f"{args.api}/health")
    ok &= check_url('API version', f"{args.api}/version")
    ok &= check_url('API metrics', f"{args.api}/metrics")
    ok &= check_url('Web root', args.web)

    if not ok:
        sys.exit(1)
    print('Smoke tests OK')


if __name__ == '__main__':
    main()

