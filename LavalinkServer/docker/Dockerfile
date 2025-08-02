FROM eclipse-temurin:18-jre-jammy

# Install necessary tools and create non-root user
RUN groupadd -g 322 lavalink && \
    useradd -r -u 322 -g lavalink lavalink && \
    apt-get update && apt-get install -y wget curl net-tools procps

# Set working directory
WORKDIR /opt/Lavalink

# Copy application files
COPY LavalinkServer/jar/Lavalink.jar Lavalink.jar
COPY application.yml ./application.yml

# Set proper permissions
RUN chown -R lavalink:lavalink /opt/Lavalink && \
    mkdir -p /opt/Lavalink/logs && \
    chown -R lavalink:lavalink /opt/Lavalink/logs

# Expose the Lavalink port
EXPOSE 2333

# Environment variables with default values
ENV LAVALINK_PASSWORD=admin123 \
    SERVER_PORT=2333 \
    SERVER_ADDRESS=0.0.0.0 \
    YOUTUBE_SOURCE_ENABLED=true \
    SOUNDCLOUD_SOURCE_ENABLED=true \
    HEALTH_CHECK_VERBOSE=true

# Switch to non-root user
USER lavalink

# Custom health check script
COPY <<EOF /opt/Lavalink/healthcheck.sh
#!/bin/bash
set -e

# Check if health check verbosity is enabled
if [ "\$HEALTH_CHECK_VERBOSE" = "true" ]; then
    echo "Starting Lavalink Health Check..."
    echo "Checking server port availability..."
    netstat -tuln | grep :2333 || echo "Port 2333 not yet listening"
    
    echo "Attempting to fetch metrics..."
    wget --spider --server-response http://localhost:2333/metrics 2>&1 || true
    
    echo "Checking server process..."
    ps aux | grep java || echo "No Java process found"
fi

# Actual health check
wget --no-verbose --tries=1 --spider http://localhost:2333/metrics
EOF

# Make the health check script executable
RUN chmod +x /opt/Lavalink/healthcheck.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD /opt/Lavalink/healthcheck.sh

# Run the application
ENTRYPOINT ["java", "-jar", "Lavalink.jar"]
