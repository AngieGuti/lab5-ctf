#!/usr/bin/env python3
"""
unlock.py - Mecanismo de desbloqueo de la Fase Defensiva (Reto 1).

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

# SHA-256 de FLAG{cmd_1nj3ct10n_dmz_byp4ss}
EXPECTED_FLAG_HASH = "4f8caccc3c35d319d5f56b3df828f879616c0e3331a81a9d5e2ccb17d537a8fb"

INCIDENT_REPORT = """
============================================================
[REPORTE DE INCIDENTE CSIRT - DMZ.10]
============================================================
- Evento: Ejecución remota de comandos no autorizada.
- Causa: Concatenación insegura en llamadas al sistema operativo.
- Impacto: Fuga de archivos sensibles del servidor web.

ESTRATEGIAS DE REMEDIACIÓN PROPUESTAS POR ARQUITECTURA:
* Propuesta A: Filtrado de caracteres especiales (; y &&).
* Propuesta B: Restricción exclusiva a caracteres numéricos.
* Propuesta C: Validación mediante expresión regular alfanumérica y caracteres de dominio (^[a-zA-Z0-9.-]+$).

INSTRUCCIONES DE REMEDIACIÓN:
1. Analiza el impacto de cada propuesta sobre el servicio (disponibilidad de dominios vs seguridad).
2. Edita manualmente 'app.py' utilizando el editor de texto de tu preferencia en consola.
3. Ubica el bloque de diagnóstico y activa la opción seleccionada comentando la llamada vulnerable.
============================================================

============================================================
[+] FASE OFENSIVA COMPLETADA CON ÉXITO
Usa la siguiente flag defensiva para desbloquear 'nano app.py':

FLAG{unlock_nano_cmd_defense_9812}
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
