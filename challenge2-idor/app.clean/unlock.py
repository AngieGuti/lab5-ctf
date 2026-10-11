#!/usr/bin/env python3
"""
unlock.py - Mecanismo de desbloqueo de la Fase Defensiva (Reto 2).

Este script:

    1. Solicita la flag obtenida en la Fase Ofensiva.
    2. Si es incorrecta, muestra un error y termina con código 1.
    3. Si es correcta, imprime el informe de incidente y muestra la
       flag defensiva para nano y termina con código 0. No modifica
       permisos ni abre ningún editor.

Se compara el hash SHA-256 de la flag, no el texto plano.

Uso:
    python unlock.py
"""

import hashlib
import sys

# SHA-256 de FLAG{1d0r_br0k3n_4cc3ss_c0ntr0l}
EXPECTED_FLAG_HASH = "2311bfc62ecdbe3af4e04c80e7ae09ea4bb8121e9d1f3db6783393e6f5c38063"

INCIDENT_REPORT = """
============================================================
[REPORTE DE INCIDENTE CSIRT - SISTEMA DE REPORTES]
============================================================
- Evento: Fuga de información confidencial de auditoría.
- Causa: Falla de control de acceso a nivel de objeto (IDOR).
- Impacto: Usuarios con rol 'auditor' acceden a datos de administración.

ESTRATEGIAS DE REMEDIACIÓN PROPUESTAS POR ARQUITECTURA:
* Propuesta 1: Validación de estado de sesión (verificar existencia de cookie activa).
* Propuesta 2: Validación estricta de propiedad (correlacionar identificador del registro con el usuario autenticado).
* Propuesta 3: Validación de formato y rango numérico del identificador del reporte.

INSTRUCCIONES DE REMEDIACIÓN:
1. Edita manualmente 'app.py' utilizando el editor de texto en consola.
2. Ubica las funciones de consulta (/report y /api/report) tras la recuperación del registro.
3. Evalúa cada propuesta y activa en el bloque [TODO DEFENSA] la opción que mitigue la fuga.
============================================================

============================================================
[+] FASE OFENSIVA COMPLETADA CON ÉXITO
Usa la siguiente flag defensiva para desbloquear 'nano app.py':

FLAG{unlock_nano_idor_defense_3421}
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

    try:
        print(INCIDENT_REPORT)
    except UnicodeEncodeError:
        print(INCIDENT_REPORT.encode("ascii", errors="replace").decode("ascii"))

    sys.exit(0)


if __name__ == "__main__":
    main()
