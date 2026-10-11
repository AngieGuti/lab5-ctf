#!/bin/bash
# reset.sh - Restaura el estado inicial (vulnerable) de los retos del
# laboratorio, copiando las versiones originales desde app.clean/ sobre
# las carpetas app/ activas de cada reto.
#
# Como docker-compose.yml monta ./challengeX/app como volumen dentro del
# contenedor, y Flask corre en modo debug (autoreload), los cambios se
# reflejan de inmediato sin necesidad de reconstruir ni reiniciar nada.
#
# Uso:
#   ./reset.sh

set -e

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR"

# a) Reto 1 - Command Injection
cp "challenge1-injection/app.clean/app.py" "challenge1-injection/app/app.py"

# b) Reto 2 - IDOR / Broken Access Control
cp challenge2-idor/app.clean/* challenge2-idor/app/

# c) Mensaje de confirmación
echo "[+] Entorno reiniciado con éxito para el siguiente grupo"
