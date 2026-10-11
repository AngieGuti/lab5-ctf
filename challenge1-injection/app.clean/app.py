"""
DMZ.10 - Herramienta Interna de Diagnóstico de Red
----------------------------------------------------
Lab5 CTF - Reto 1: Command Injection

⚠️ VERSION VULNERABLE (a propósito, para fines docentes) ⚠️

Este endpoint ejecuta un "ping" hacia el host indicado por el usuario,
pero construye el comando de forma insegura concatenando texto y
ejecutándolo con shell=True. Esto permite inyección de comandos del
sistema operativo (OS Command Injection).

Objetivo del reto (ofensivo):
    Enviar un payload como:
        127.0.0.1; cat flag.txt
    o bien:
        127.0.0.1 && cat flag.txt
    para que el servidor ejecute un comando adicional y revele el
    contenido de flag.txt.

Objetivo del reto (defensivo):
    Editar este archivo (correr dentro del contenedor vía ttyd en
    /app/app.py) para reemplazar la construcción insegura del comando
    por una llamada segura usando subprocess.run con una lista de
    argumentos, más validación de entrada (regex / módulo ipaddress),
    de forma que la inyección ya no sea posible.

    Una copia de referencia de esta versión vulnerable original queda
    guardada en app.clean/app.py por si se necesita restaurar el reto.
"""

from flask import Flask, request, render_template
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
    command = "ping -c 1 " + host
    output = os.popen(command).read()
    # --- FIN BLOQUE VULNERABLE -----------------------------------------

    if request.is_json:
        return {"host": host, "output": output}

    return render_template("index.html", output=output, host=host)


if __name__ == "__main__":
    # debug=True habilita recarga automática (hot-reload) para que los
    # cambios que el estudiante haga en app.py se reflejen sin reiniciar
    # manualmente el contenedor.
    app.run(host="0.0.0.0", port=5001, debug=True)
