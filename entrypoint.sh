#!/bin/bash

# Function to check Lavalink connectivity
check_lavalink() {
    # Try multiple connection methods with IP
    docker_ip=$(getent hosts lavalink | awk '{ print $1 }')
    
    if [ -z "$docker_ip" ]; then
        echo "Could not resolve Lavalink IP"
        return 1
    fi

    # Method 1: Direct IP connection
    timeout 5 bash -c "</dev/tcp/$docker_ip/2333" 2>/dev/null && return 0

    # Method 2: Curl with IP
    curl -s --max-time 5 "http://$docker_ip:2333/metrics" > /dev/null && return 0

    # Method 3: Python socket with IP
    python3 -c "
import socket
import sys

try:
    socket.create_connection(('$docker_ip', 2333), timeout=5)
    sys.exit(0)
except Exception:
    sys.exit(1)
" && return 0

    # All methods failed
    return 1
}

# Maximum wait time (in seconds)
MAX_WAIT=300
WAIT_INTERVAL=10
ELAPSED_TIME=0

echo "Waiting for Lavalink to be ready..."
echo "Attempting to resolve Lavalink container IP..."

# Wait loop with timeout
while [ $ELAPSED_TIME -lt $MAX_WAIT ]; do
    # Get Docker network details
    echo "Network Debug:"
    docker network ls
    docker network inspect lavalink_network

    # Resolve IP
    docker_ip=$(getent hosts lavalink | awk '{ print $1 }')
    echo "Resolved Lavalink IP: $docker_ip"

    if [ -n "$docker_ip" ]; then
        if check_lavalink; then
            echo "Lavalink is up and running!"
            break
        fi
    fi

    echo "Waiting for Lavalink (${ELAPSED_TIME}s/${MAX_WAIT}s)..."
    sleep $WAIT_INTERVAL
    ELAPSED_TIME=$((ELAPSED_TIME + WAIT_INTERVAL))
done

# Check if we timed out
if [ $ELAPSED_TIME -ge $MAX_WAIT ]; then
    echo "ERROR: Lavalink did not become ready within ${MAX_WAIT} seconds"
    
    # Detailed debugging
    echo "Container Status:"
    docker ps
    
    echo "Lavalink Container Logs:"
    docker logs lavalink
    
    exit 1
fi

# Start the Flask application
echo "Starting Lavalink Dashboard..."
exec flask run --host=0.0.0.0 --port=5000 --proxy-headers