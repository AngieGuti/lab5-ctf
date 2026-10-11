FROM python:3.11-slim

# --- Dependencias de sistema -------------------------------------------
# - curl/bash: utilidades básicas de terminal.
# - ttyd: terminal web embebida para que el estudiante edite app.py en vivo.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        bash \
        procps \
        nano \
        sqlite3 \
    && mv /usr/bin/nano /usr/bin/nano.bin \
    && rm -rf /var/lib/apt/lists/*

# Wrapper de seguridad: /usr/bin/nano pide la flag defensiva antes de
# ejecutar el binario real (/usr/bin/nano.bin).
ENV NANO_UNLOCK_FLAG="FLAG{unlock_nano_idor_defense_3421}"
COPY nano-wrapper.sh /usr/bin/nano
RUN sed -i 's/[[:cntrl:]]$//' /usr/bin/nano \
    && chmod 755 /usr/bin/nano

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
RUN chown -R student:student /app /app.clean \
    && chmod 444 /app/app.py /app.clean/app.py

# Script de arranque: levanta Flask (puerto 5002) y ttyd (puerto 7682)
COPY entrypoint.sh /entrypoint.sh
COPY ttyd-welcome.sh /usr/local/bin/ttyd-welcome.sh
RUN chmod +x /entrypoint.sh /usr/local/bin/ttyd-welcome.sh

# Nota: no se fija USER aquí a propósito. El contenedor arranca como
# root para que entrypoint.sh pueda corregir la propiedad de /app
# (necesario en bind mounts donde el host no preserva el UID de
# 'student'), pero Flask y ttyd se ejecutan como 'student' vía 'su'
# dentro de entrypoint.sh — nunca se expone un proceso corriendo como
# root.

EXPOSE 5002 7682

ENTRYPOINT ["/entrypoint.sh"]
