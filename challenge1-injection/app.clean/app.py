"""
DMZ.10 - Herramienta Interna de Diagnóstico de Red
----------------------------------------------------
Lab5 CTF - Reto 1: Command Injection

⚠️ VERSION VULNERABLE (a propósito, para fines docentes) ⚠️

Este endpoint ejecuta un "ping" hacia el host indicado por el usuario,
pero construye el comando de forma insegura concatenando texto y
ejecutándolo con shell=True (vía os.popen). Esto permite inyección de
comandos del sistema operativo (OS Command Injection).

Objetivo del reto (ofensivo):
    Enviar un payload como:
        127.0.0.1; cat flag.txt
    o bien:
        127.0.0.1 && cat flag.txt
    para que el servidor ejecute un comando adicional y revele el
    contenido de flag.txt.

Objetivo del reto (defensivo):
    Editar este archivo (vía ttyd en http://<host>:7681, con
    'nano app.py' dentro de /app) siguiendo las instrucciones del
    bloque marcado [TODO DEFENSA] más abajo, para reemplazar la
    construcción insegura del comando por una llamada segura usando
    subprocess.run con una lista de argumentos, más validación de
    entrada.

    Una copia de referencia de esta versión vulnerable original queda
    guardada en app.clean/app.py por si se necesita restaurar el reto.
"""

from flask import Flask, request, render_template
import subprocess
import re
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", output=None, host=None)


@app.route("/diagnostic", methods=["GET", "POST"])
def diagnostic():
    """
    Endpoint vulnerable a Command Injection.

    Acepta el host/IP a diagnosticar vía parámetro 'host' (o 'ip' como
    alias, para compatibilidad) tanto en POST (formulario web) como en
    GET/POST (JSON), y ejecuta un ping usando shell=True sin ninguna
    sanitización ni validación de la entrada del usuario.
    """
    if request.is_json:
        data = request.get_json(silent=True) or {}
        host = data.get("host") or data.get("ip") or ""
    else:
        host = request.form.get("host") or request.form.get("ip") or request.args.get("host") or request.args.get("ip") or ""

    if not host:
        if request.is_json:
            return {"error": "Debe proporcionar 'host' o 'ip'"}, 400
        return render_template("index.html", output=None, host=None)

    # --- INICIO BLOQUE VULNERABLE -------------------------------------
    # Construcción insegura del comando: concatenación directa de la
    # entrada del usuario dentro de un comando de shell.
    # Un atacante puede inyectar comandos adicionales usando ';', '&&',
    # '|', backticks, etc.
    output = os.popen("ping -c 1 " + host).read()

    # ========================================================
    # [TODO DEFENSA]: MITIGACIÓN DE COMMAND INJECTION
    # 1. Comenta la línea os.popen anterior.
    # 2. Completa la condición if not para rechazar hosts con caracteres inválidos.
    # 3. Descomenta el bloque subprocess.run seguro ya preparado:
    #
    # if not re.match(r"^[a-zA-Z0-9.-]+$", host):
    #     output = "Error: Caracteres no permitidos en el host."
    # else:
    #     res = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True, timeout=3)
    #     output = res.stdout or res.stderr
    # ========================================================
    # --- FIN BLOQUE VULNERABLE -----------------------------------------

    if request.is_json:
        return {"host": host, "output": output}

    return render_template("index.html", output=output, host=host)


if __name__ == "__main__":
    # debug=True habilita recarga automática (hot-reload) para que los
    # cambios que el estudiante haga en app.py se reflejen sin reiniciar
    # manualmente el contenedor.
    app.run(host="0.0.0.0", port=5001, debug=True)
