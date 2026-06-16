#!/bin/bash
echo "Starting PRM Server..."

# Uncomment and fill these in to enable the Gmail SMTP integration
export SMTP_USER="kritikajain5524@gmail.com"
export SMTP_PASSWORD="svuv ifqn xdxy kdoi"

# Navigate to the directory containing this script, then start the server
cd "$(dirname "$0")"
uvicorn server.main:app --reload
