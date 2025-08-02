FROM eclipse-temurin:18-jdk-jammy AS builder

WORKDIR /app

COPY . .

RUN ./gradlew build --no-daemon

# ===== Runtime Image =====
FROM eclipse-temurin:18-jre-jammy

RUN groupadd -g 322 lavalink && \
    useradd -r -u 322 -g lavalink lavalink

WORKDIR /opt/Lavalink
COPY --from=builder /app/LavalinkServer/build/libs/Lavalink.jar Lavalink.jar

RUN chown -R lavalink:lavalink /opt/Lavalink
USER lavalink

ENTRYPOINT ["java", "-jar", "Lavalink.jar"]
