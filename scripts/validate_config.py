#!/usr/bin/env python3
import sys
try:
    from src.core.engine.settings import settings
except ImportError:
    print("ERROR: Could not import settings from src.core.engine.settings. Make sure you run this from the project root.")
    sys.exit(2)

errors = settings.validate()
if errors:
    print("Configuration validation errors:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("Config OK")
    sys.exit(0)
