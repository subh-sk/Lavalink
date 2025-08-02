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

# Create health check script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Check if health check verbosity is enabled\n\
if [ "$HEALTH_CHECK_VERBOSE" = "true" ]; then\n\
    echo "Starting Lavalink Health Check..."\n\
    echo "Checking server port availability..."\n\
    netstat -tuln | grep :2333 || echo "Port 2333 not yet listening"\n\
    \n\
    echo "Attempting to fetch metrics..."\n\
    wget --spider --server-response http://localhost:2333/metrics 2>&1 || true\n\
    \n\
    echo "Checking server process..."\n\
    ps aux | grep java || echo "No Java process found"\n\
fi\n\
\n\
# Actual health check\n\
wget --no-verbose --tries=1 --spider http://localhost:2333/metrics\n\
' > /opt/Lavalink/healthcheck.sh && \
    chmod +x /opt/Lavalink/healthcheck.sh

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
    HEALTH_CHECK_VERBOSE=true \
    SENTRY_DSN="" \
    SENTRY_ENVIRONMENT=""

# Switch to non-root user
USER lavalink

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD /opt/Lavalink/healthcheck.sh

# Run the application
ENTRYPOINT ["java", "-jar", "Lavalink.jar"]
