#!/usr/bin/env python

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

# This is required for Vercel
if __name__ == "__main__":
    app
