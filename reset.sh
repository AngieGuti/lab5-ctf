#!/bin/bash
# reset.sh - Restaura el estado inicial (vulnerable + bloqueado) de los
# retos del laboratorio, copiando las versiones originales desde
# app.clean/ sobre las carpetas app/ activas de cada reto, y volviendo
# a dejar app.py en modo SOLO LECTURA (chmod 444) para el siguiente
# grupo (debe ejecutar unlock.py con la flag correcta para editarlo).
#
# Como docker-compose.yml monta ./challengeX/app como volumen dentro del
# contenedor, y Flask corre en modo debug (autoreload), los cambios se
# reflejan de inmediato sin necesidad de reconstruir ni reiniciar nada.
#
# Nota: este archivo debe mantenerse con saltos de línea LF (Unix). Si
# se edita desde Windows con un editor que use CRLF, puede fallar al
# ejecutarse dentro de WSL/Git Bash/contenedores Linux. Si existe una
# alternativa multiplataforma, usar reset.py (python reset.py).
#
# Uso:
#   ./reset.sh
#   bash reset.sh

set -e

# Evita que Git Bash / MSYS en Windows convierta rutas tipo '/app/...'
# en rutas de Windows al invocar docker.exe (rompería los 'docker exec'
# de más abajo). No tiene efecto en Linux/macOS.
export MSYS_NO_PATHCONV=1

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR"

# a) Reto 1 - Command Injection (reemplazo forzado, sin preguntar)
cp -f "challenge1-injection/app.clean/app.py" "challenge1-injection/app/app.py"
cp -f "challenge1-injection/app.clean/unlock.py" "challenge1-injection/app/unlock.py"

# b) Reto 2 - IDOR / Broken Access Control (reemplazo forzado, sin preguntar)
cp -f challenge2-idor/app.clean/app.py challenge2-idor/app/app.py
cp -f challenge2-idor/app.clean/unlock.py challenge2-idor/app/unlock.py
cp -f challenge2-idor/app.clean/database.sqlite challenge2-idor/app/database.sqlite

# Permisos: unlock.py queda ejecutable; app.py vuelve a SOLO LECTURA
# (444) hasta que el siguiente grupo ejecute unlock.py con la flag
# correcta.
chmod 755 challenge1-injection/app/unlock.py challenge2-idor/app/unlock.py 2>/dev/null || true
chmod 444 challenge1-injection/app/app.py challenge2-idor/app/app.py 2>/dev/null || true
chmod 664 challenge2-idor/app/database.sqlite 2>/dev/null || true

# Refuerzo: en algunos hosts (p. ej. bind mounts de Docker Desktop en
# Windows) sobrescribir el archivo desde fuera del contenedor hace que
# vuelva a aparecer como propiedad de 'root' dentro de él (en vez de
# 'student'), lo que haría fallar el chmod que hace unlock.py la
# siguiente vez. Si los contenedores están corriendo, se repite el
# chown + chmod también desde dentro, vía docker exec (como root, ya
# que el contenedor no fija USER por defecto).
relock_container() {
    local container="$1"
    local attempt
    for attempt in 1 2 3; do
        if docker exec "$container" chown student:student /app/app.py >/dev/null 2>&1 \
           && docker exec "$container" chmod 444 /app/app.py >/dev/null 2>&1; then
            return 0
        fi
        sleep 0.5
    done
    return 1
}

if command -v docker >/dev/null 2>&1; then
    relock_container ctf-challenge1-injection || true
    relock_container ctf-challenge2-idor || true
fi

# c) Mensaje de confirmación
echo "[+] Entorno reiniciado con éxito para el siguiente grupo"
