FROM eclipse-temurin:18-jre-jammy

# Install necessary tools and create non-root user
RUN groupadd -g 322 lavalink && \
    useradd -r -u 322 -g lavalink lavalink && \
    apt-get update && apt-get install -y wget

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
    YOUTUBE_SOURCE_ENABLED=false \
    SOUNDCLOUD_SOURCE_ENABLED=true

# Switch to non-root user
USER lavalink

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:2333/metrics || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "Lavalink.jar"]
