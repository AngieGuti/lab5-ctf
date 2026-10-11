#!/bin/bash
# reset.sh - Restaura el estado inicial (vulnerable) de los retos y
# reconstruye/reinicia los contenedores del laboratorio.
#
# Uso:
#   ./reset.sh              -> resetea todos los retos
#   ./reset.sh challenge1   -> resetea solo el reto 1

set -e

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR"

reset_challenge1() {
    echo "[*] Restaurando app.py original (vulnerable) del Reto 1..."
    cp "challenge1-injection/app.clean/app.py" "challenge1-injection/app/app.py"
    echo "[*] Reto 1 restaurado."
}

TARGET="${1:-all}"

case "$TARGET" in
    challenge1|challenge1-injection)
        reset_challenge1
        ;;
    all)
        reset_challenge1
        ;;
    *)
        echo "Objetivo desconocido: $TARGET"
        echo "Uso: ./reset.sh [challenge1|all]"
        exit 1
        ;;
esac

echo "[*] Reconstruyendo y reiniciando contenedores con docker-compose..."
docker-compose down
docker-compose up -d --build

echo "[*] Listo. Reto 1 disponible en:"
echo "    - App:      http://localhost:5001"
echo "    - Terminal: http://localhost:7681"
