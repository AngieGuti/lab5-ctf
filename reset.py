#!/usr/bin/env python3
"""
reset.py - Alternativa multiplataforma a reset.sh.

Restaura el estado inicial (vulnerable + bloqueado) de los retos del
laboratorio, copiando las versiones originales desde app.clean/ sobre
las carpetas app/ activas de cada reto, usando shutil.copyfile (evita
depender de 'cp' y de la disponibilidad de un shell POSIX, lo cual es
útil en Windows sin Git Bash / WSL, o en cualquier entorno donde
'bash reset.sh' no esté disponible).

Además, vuelve a dejar app.py en modo SOLO LECTURA (chmod 444) en
ambos retos, para que el siguiente grupo deba ejecutar 'unlock.py' con
la flag correcta antes de poder editarlo.

Como docker-compose.yml monta ./challengeX/app como volumen dentro del
contenedor, y Flask corre en modo debug (autoreload), los cambios se
reflejan de inmediato sin necesidad de reconstruir ni reiniciar nada.

Uso:
    python reset.py
    python3 reset.py
"""

import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent

# Cada tupla es (origen en app.clean/, destino en app/)
FILES_TO_RESTORE = [
    (
        LAB_DIR / "challenge1-injection" / "app.clean" / "app.py",
        LAB_DIR / "challenge1-injection" / "app" / "app.py",
    ),
    (
        LAB_DIR / "challenge1-injection" / "app.clean" / "unlock.py",
        LAB_DIR / "challenge1-injection" / "app" / "unlock.py",
    ),
    (
        LAB_DIR / "challenge2-idor" / "app.clean" / "app.py",
        LAB_DIR / "challenge2-idor" / "app" / "app.py",
    ),
    (
        LAB_DIR / "challenge2-idor" / "app.clean" / "unlock.py",
        LAB_DIR / "challenge2-idor" / "app" / "unlock.py",
    ),
    (
        LAB_DIR / "challenge2-idor" / "app.clean" / "database.sqlite",
        LAB_DIR / "challenge2-idor" / "app" / "database.sqlite",
    ),
]

# app.py de ambos retos vuelve a modo SOLO LECTURA (444) tras el reset.
APP_PY_FILES_TO_LOCK = [
    LAB_DIR / "challenge1-injection" / "app" / "app.py",
    LAB_DIR / "challenge2-idor" / "app" / "app.py",
]

# unlock.py queda ejecutable (755) para que el siguiente grupo lo corra.
UNLOCK_PY_FILES = [
    LAB_DIR / "challenge1-injection" / "app" / "unlock.py",
    LAB_DIR / "challenge2-idor" / "app" / "unlock.py",
]


def restore_file(src: Path, dst: Path) -> None:
    if not src.is_file():
        print(f"[!] No se encontró el archivo de respaldo: {src}", file=sys.stderr)
        sys.exit(1)
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Si el destino ya existe y quedó en modo solo lectura (p. ej.
    # app.py bloqueado con chmod 444 de una ronda anterior), hay que
    # habilitar escritura antes de sobrescribirlo: en Windows,
    # shutil.copyfile falla con PermissionError sobre un archivo
    # destino de solo lectura, a diferencia de 'cp -f' en Unix.
    if dst.exists():
        try:
            dst.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
        except OSError:
            pass

    shutil.copyfile(src, dst)


def chmod_safe(path: Path, mode: int) -> None:
    try:
        path.chmod(mode)
    except OSError as exc:
        # No interrumpe el reset si el sistema de archivos del host
        # (p. ej. un volumen de Windows) no soporta estos bits.
        print(f"[!] No se pudo ajustar permisos de {path}: {exc}", file=sys.stderr)


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


CONTAINER_NAMES = ["ctf-challenge1-injection", "ctf-challenge2-idor"]


def relock_inside_containers() -> None:
    """
    Refuerzo: en algunos hosts (p. ej. bind mounts de Docker Desktop en
    Windows) sobrescribir el archivo desde fuera del contenedor hace
    que vuelva a aparecer como propiedad de 'root' dentro de él (en vez
    de 'student'), lo que haría fallar el chmod que hace unlock.py la
    siguiente vez. Si los contenedores están corriendo, se repite el
    chown + chmod también desde dentro, vía 'docker exec' (como root,
    ya que el contenedor no fija USER por defecto). No falla el script
    si docker no está disponible o el contenedor no corre.
    """
    docker = shutil.which("docker")
    if docker is None:
        return

    def run_ok(cmd: list) -> bool:
        try:
            return subprocess.run(cmd, capture_output=True, timeout=10).returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    for name in CONTAINER_NAMES:
        # Pequeño reintento: justo después de sobrescribir el archivo
        # desde el host, el bind mount puede tardar un instante en
        # propagar el cambio al contenedor.
        for _ in range(3):
            chown_ok = run_ok([docker, "exec", name, "chown", "student:student", "/app/app.py"])
            chmod_ok = run_ok([docker, "exec", name, "chmod", "444", "/app/app.py"])
            if chown_ok and chmod_ok:
                break
            time.sleep(0.5)


def main() -> None:
    for src, dst in FILES_TO_RESTORE:
        restore_file(src, dst)

    # app.py bloqueado (solo lectura) hasta que se ejecute unlock.py.
    for app_py in APP_PY_FILES_TO_LOCK:
        chmod_safe(app_py, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # 444

    relock_inside_containers()

    # unlock.py ejecutable para el siguiente grupo.
    for unlock_py in UNLOCK_PY_FILES:
        chmod_safe(
            unlock_py,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
            | stat.S_IRGRP | stat.S_IXGRP
            | stat.S_IROTH | stat.S_IXOTH,
        )  # 755

    safe_print("[+] Entorno reiniciado con éxito para el siguiente grupo")


if __name__ == "__main__":
    main()
