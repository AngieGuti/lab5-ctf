#!/bin/bash
# reset.sh - Restaura el estado inicial (vulnerable) de los retos del
# laboratorio, copiando las versiones originales desde app.clean/ sobre
# las carpetas app/ activas de cada reto.
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

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR"

# a) Reto 1 - Command Injection (reemplazo forzado, sin preguntar)
cp -f "challenge1-injection/app.clean/app.py" "challenge1-injection/app/app.py"

# b) Reto 2 - IDOR / Broken Access Control (reemplazo forzado, sin preguntar)
cp -f challenge2-idor/app.clean/app.py challenge2-idor/app/app.py
cp -f challenge2-idor/app.clean/database.sqlite challenge2-idor/app/database.sqlite

# Asegura permisos de lectura/escritura esperados tras la copia
chmod 644 challenge1-injection/app/app.py challenge2-idor/app/app.py challenge2-idor/app/database.sqlite 2>/dev/null || true

# c) Mensaje de confirmación
echo "[+] Entorno reiniciado con éxito para el siguiente grupo"
