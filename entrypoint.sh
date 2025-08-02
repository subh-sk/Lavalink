#!/bin/bash

# Function to check Lavalink connectivity
check_lavalink() {
    # Method 1: Check TCP connection
    nc -z lavalink 2333 && return 0

    # Method 2: Use curl to check HTTP endpoint
    curl -s http://lavalink:2333/metrics > /dev/null && return 0

    # Method 3: Use Python to check connection
    python3 -c "
import socket
import sys

try:
    socket.create_connection(('lavalink', 2333), timeout=5)
    sys.exit(0)
except (socket.timeout, ConnectionRefusedError):
    sys.exit(1)
" && return 0

    # All methods failed
    return 1
}

# Maximum wait time (in seconds)
MAX_WAIT=120
WAIT_INTERVAL=5
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

# Additional diagnostic information
echo "Lavalink Connectivity Check:"
nc -z lavalink 2333 && echo "TCP Port 2333: Open" || echo "TCP Port 2333: Closed"
curl -s http://lavalink:2333/metrics > /dev/null && echo "HTTP Metrics: Accessible" || echo "HTTP Metrics: Not Accessible"

# Start the Flask application
echo "Starting Lavalink Dashboard..."
exec flask run --host=0.0.0.0 --port=5000 --proxy-headers