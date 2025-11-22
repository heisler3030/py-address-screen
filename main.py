#!/usr/bin/env python3
"""
py-address-screen: A Python utility for cryptocurrency address screening using Chainalysis API.

This module provides the main entry point for the address screening application.
"""

import sys
from pathlib import Path

# Add the package directory to Python path
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))

from py_address_screen import main

if __name__ == "__main__":
    main()