#!/bin/bash

# Simple connectivity check function
check_lavalink() {
    # Try to connect to Lavalink
    timeout 5 bash -c "</dev/tcp/lavalink/2333" 2>/dev/null
}

# Maximum wait time (in seconds)
MAX_WAIT=300
WAIT_INTERVAL=10
ELAPSED_TIME=0

echo "Waiting for Lavalink to be ready..."

# Wait loop with timeout
while [ $ELAPSED_TIME -lt $MAX_WAIT ]; do
    if check_lavalink; then
        echo "Lavalink is up and running!"
        break
    fi

    echo "Waiting for Lavalink (${ELAPSED_TIME}s/${MAX_WAIT}s)..."
    sleep $WAIT_INTERVAL
    ELAPSED_TIME=$((ELAPSED_TIME + WAIT_INTERVAL))
done

# Check if we timed out
if [ $ELAPSED_TIME -ge $MAX_WAIT ]; then
    echo "ERROR: Lavalink did not become ready within ${MAX_WAIT} seconds"
    exit 1
fi

# Start the Flask application
echo "Starting Lavalink Dashboard..."
exec flask run --host=0.0.0.0 --port=5000 --proxy-headers