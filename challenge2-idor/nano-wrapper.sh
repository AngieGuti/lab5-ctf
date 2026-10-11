#!/bin/bash
# Wrapper de seguridad para interceptar nano
TARGET_FLAG="$NANO_UNLOCK_FLAG"

echo "============================================================"
echo "[BLOQUEO CSIRT] Edición de código restringida"
echo "============================================================"
read -r -p "Ingrese la flag defensiva de desbloqueo: " INPUT_FLAG

if [ -n "$TARGET_FLAG" ] && [ "$INPUT_FLAG" = "$TARGET_FLAG" ]; then
    echo "[+] Flag defensiva validada. Abriendo editor..."
    exec /usr/bin/nano.bin "$@"
else
    echo "[!] ACCESO DENEGADO: Flag incorrecta."
    echo "[!] Debes resolver la Fase 1 y ejecutar 'python unlock.py' para obtenerla."
    exit 1
fi
