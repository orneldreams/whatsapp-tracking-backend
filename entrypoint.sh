#!/bin/bash
# Entrypoint script for Railway deployment

# Set default port if not provided
PORT=${PORT:-8000}

# Run uvicorn with the port from environment
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
