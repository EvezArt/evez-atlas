#!/usr/bin/env python3
"""
EVEZ Tokenless Code Generator — Termux CLI Wrapper
Installs as 'evez-gen' command on Android via Termux.

Usage:
  python3 evez_gen.py <pattern> [options]
  # Or after install:
  evez-gen <pattern> [options]

Install:
  pip install -e .  (or just symlink)
"""

import sys
import os

# Add the codegen module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evez_codegen import cli_main, print_help

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    sys.exit(cli_main(sys.argv))
