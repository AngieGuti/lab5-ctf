FROM python:3.11-slim

# --- Dependencias de sistema -------------------------------------------
# - ping (iputils-ping): necesario para que el comando de diagnóstico exista.
# - curl/bash: utilidades básicas de terminal.
# - ttyd: terminal web embebida para que el estudiante edite app.py en vivo.
RUN apt-get update && apt-get install -y --no-install-recommends \
        iputils-ping \
        curl \
        bash \
        procps \
        nano \
        vim \
    && rm -rf /var/lib/apt/lists/*

# Instalación de ttyd (binario estático desde GitHub releases)
RUN ARCH="$(dpkg --print-architecture)" \
    && case "$ARCH" in \
        amd64) TTYD_ARCH="x86_64" ;; \
        arm64) TTYD_ARCH="aarch64" ;; \
        *) TTYD_ARCH="x86_64" ;; \
       esac \
    && curl -fsSL -o /usr/local/bin/ttyd \
        "https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.${TTYD_ARCH}" \
    && chmod +x /usr/local/bin/ttyd

# --- Dependencias Python -------------------------------------------------
RUN pip install --no-cache-dir flask

# --- Usuario estándar (no root) con permisos de edición sobre /app -------
RUN useradd -ms /bin/bash student
WORKDIR /app
COPY app/ /app/
COPY app.clean/ /app.clean/
RUN chown -R student:student /app /app.clean

# Script de arranque: levanta Flask (puerto 5001) y ttyd (puerto 7681)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER student

EXPOSE 5001 7681

ENTRYPOINT ["/entrypoint.sh"]
