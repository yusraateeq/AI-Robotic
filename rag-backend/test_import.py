#!/usr/bin/env python3
import sys

print("Testing imports...")
try:
    from main import app
    print("✓ main.py imports OK")
except Exception as e:
    print(f"✗ main.py import failed: {e}")
    import traceback
    traceback.print_exc()
