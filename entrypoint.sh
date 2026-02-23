#!/usr/bin/env python3
import os
import subprocess
import sys

# Get port from environment or default to 8000
port = os.environ.get('PORT', '8000')

# Run uvicorn
subprocess.call([
    'uvicorn',
    'app.main:app',
    '--host', '0.0.0.0',
    '--port', port
])
