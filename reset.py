#!/usr/bin/env python3
"""
reset.py - Alternativa multiplataforma a reset.sh.

Restaura el estado inicial (vulnerable) de los retos del laboratorio,
copiando las versiones originales desde app.clean/ sobre las carpetas
app/ activas de cada reto, usando shutil.copyfile (evita depender de
'cp' y de la disponibilidad de un shell POSIX, lo cual es útil en
Windows sin Git Bash / WSL, o en cualquier entorno donde 'bash
reset.sh' no esté disponible).

Como docker-compose.yml monta ./challengeX/app como volumen dentro del
contenedor, y Flask corre en modo debug (autoreload), los cambios se
reflejan de inmediato sin necesidad de reconstruir ni reiniciar nada.

Uso:
    python reset.py
    python3 reset.py
"""

import shutil
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent

# Cada tupla es (origen en app.clean/, destino en app/)
FILES_TO_RESTORE = [
    (
        LAB_DIR / "challenge1-injection" / "app.clean" / "app.py",
        LAB_DIR / "challenge1-injection" / "app" / "app.py",
    ),
    (
        LAB_DIR / "challenge2-idor" / "app.clean" / "app.py",
        LAB_DIR / "challenge2-idor" / "app" / "app.py",
    ),
    (
        LAB_DIR / "challenge2-idor" / "app.clean" / "database.sqlite",
        LAB_DIR / "challenge2-idor" / "app" / "database.sqlite",
    ),
]


def restore_file(src: Path, dst: Path) -> None:
    if not src.is_file():
        print(f"[!] No se encontró el archivo de respaldo: {src}", file=sys.stderr)
        sys.exit(1)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def safe_print(message: str) -> None:
    """
    Imprime el mensaje intentando preservar tildes/acentos, pero sin
    fallar si la consola (p. ej. cmd.exe en Windows con un codepage
    heredado) no puede codificar esos caracteres.
    """
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", errors="replace").decode("ascii"))


def main() -> None:
    for src, dst in FILES_TO_RESTORE:
        restore_file(src, dst)

    safe_print("[+] Entorno reiniciado con éxito para el siguiente grupo")


if __name__ == "__main__":
    main()
