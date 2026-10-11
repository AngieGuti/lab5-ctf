#!/usr/bin/env python3
"""
unlock.py - Mecanismo de desbloqueo de la Fase Defensiva (Reto 2).

app.py arranca en modo SOLO LECTURA (chmod 444) para forzar a que el
grupo explote primero la vulnerabilidad de IDOR y obtenga la flag.
Este script:

    1. Solicita la flag obtenida en la Fase Ofensiva.
    2. Si es incorrecta, muestra un aviso y termina (código de salida 1).
    3. Si es correcta:
        a) Imprime un breve reporte de incidente (estilo CSIRT).
        b) Habilita permisos de escritura sobre app.py (chmod 664).
        c) Abre app.py en nano automáticamente.

Nota: se compara el hash SHA-256 de la flag, no la flag en texto
plano, para que no sea trivial "hacer trampa" leyendo este archivo.

Uso:
    python unlock.py
"""

import hashlib
import os
import stat
import subprocess
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PY = os.path.join(APP_DIR, "app.py")

# SHA-256 de FLAG{1d0r_br0k3n_4cc3ss_c0ntr0l}
EXPECTED_FLAG_HASH = "2311bfc62ecdbe3af4e04c80e7ae09ea4bb8121e9d1f3db6783393e6f5c38063"

INCIDENT_REPORT = """
================================================================
 ALERTA DE INCIDENTE CSIRT
================================================================
 Fuga de informacion confidencial.

 Causa raiz : Falla de control de acceso a nivel de objeto (IDOR).
 Impacto    : Visualizacion no autorizada de reportes del
              administrador.
 Accion     : Verificar que session['user_id'] coincida con el
              propietario del recurso antes de responder.
================================================================
"""


def flag_is_correct(flag: str) -> bool:
    digest = hashlib.sha256(flag.strip().encode("utf-8")).hexdigest()
    return digest == EXPECTED_FLAG_HASH


def main() -> None:
    flag = input("Ingresa la flag obtenida en la Fase Ofensiva: ")

    if not flag_is_correct(flag):
        print("[!] Flag incorrecta. Debes explotar la vulnerabilidad primero.")
        sys.exit(1)

    print(INCIDENT_REPORT)

    # Habilita permisos de escritura sobre app.py (chmod 664)
    os.chmod(
        APP_PY,
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH,
    )

    # Abre app.py en nano para que el grupo aplique el parche
    subprocess.call(["nano", APP_PY])


if __name__ == "__main__":
    main()
