#!/bin/bash
# Load OpenClaw environment variables and run a command

ENV_FILE="$HOME/.openclaw/.env"

# Load .env file if it exists
if [ -f "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found at $ENV_FILE"
fi

# Run the command
exec "$@"
