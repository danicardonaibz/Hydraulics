#!/usr/bin/env python3
"""
Hydraulic Piping Calculation Tool
Main entry point for the CLI application
"""

import sys
from hydraulics.ui import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
