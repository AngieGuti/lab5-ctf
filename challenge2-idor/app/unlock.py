#!/usr/bin/env python3
"""
unlock.py - Mecanismo de desbloqueo de la Fase Defensiva (Reto 2).

app.py arranca en modo SOLO LECTURA (chmod 444). Este script:

    1. Solicita la flag obtenida en la Fase Ofensiva.
    2. Si es incorrecta, muestra un error y termina con código 1.
    3. Si es correcta, habilita escritura sobre app.py (chmod 664),
       imprime el informe de incidente y devuelve el control a la shell.
       No abre ningún editor: la edición la realiza el estudiante.

Se compara el hash SHA-256 de la flag, no el texto plano.

Uso:
    python unlock.py
"""

import hashlib
import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PY = os.path.join(APP_DIR, "app.py")

# SHA-256 de FLAG{1d0r_br0k3n_4cc3ss_c0ntr0l}
EXPECTED_FLAG_HASH = "2311bfc62ecdbe3af4e04c80e7ae09ea4bb8121e9d1f3db6783393e6f5c38063"

INCIDENT_REPORT = """
============================================================
[REPORTE DE INCIDENTE CSIRT - SISTEMA DE REPORTES]
============================================================
- Evento: Fuga de información confidencial de auditoría.
- Causa: Falla de control de acceso a nivel de objeto (IDOR).
- Impacto: Usuarios con rol 'auditor' acceden a datos de administración.

DIRECTIVA TÉCNICA DE SEGURIDAD:
* Principio de Verificación de Propietario:
  Ningún usuario puede consultar registros que no le pertenezcan.
  El sistema debe validar que la identidad autenticada en sesión
  coincida con el dueño del registro solicitado. En caso de discrepancia,
  debe denegar el acceso retornando error 403 Forbidden.

INSTRUCCIONES DE REMEDIACIÓN:
1. Edita manualmente 'app.py' utilizando el editor de texto en consola.
2. Ubica las funciones de consulta (/report y /api/report) tras la recuperación del registro.
3. Implementa la validación de pertenencia requerida antes de responder al cliente.
============================================================
"""


def flag_is_correct(flag: str) -> bool:
    digest = hashlib.sha256(flag.strip().encode("utf-8")).hexdigest()
    return digest == EXPECTED_FLAG_HASH


def main() -> None:
    flag = input("Ingresa la flag obtenida en la Fase Ofensiva: ")

    if not flag_is_correct(flag):
        print("[!] Flag incorrecta. Debes explotar la vulnerabilidad primero.")
        sys.exit(1)

    os.chmod(APP_PY, 0o664)

    try:
        print(INCIDENT_REPORT)
    except UnicodeEncodeError:
        print(INCIDENT_REPORT.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    main()
