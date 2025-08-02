#!/bin/bash

# Wait for Lavalink container to be ready
while ! nc -z lavalink 2333; do   
  echo "Waiting for Lavalink to launch..."
  sleep 5
done

echo "Lavalink is up - starting dashboard"
flask run --port=5000