"""
DMZ.10 - Herramienta Interna de Diagnóstico de Red
----------------------------------------------------
Lab5 CTF - Reto 1: Command Injection

⚠️ VERSION VULNERABLE (a propósito, para fines docentes) ⚠️

Este endpoint ejecuta un "ping" hacia el host indicado por el usuario,
pero construye el comando de forma insegura concatenando texto y
ejecutándolo con shell=True (vía os.popen). Esto permite inyección de
comandos del sistema operativo (OS Command Injection).

Objetivo del reto (defensivo):
    Este archivo arranca en modo SOLO LECTURA (chmod 444). Para
    desbloquearlo, sigue las instrucciones de la Fase 2 en la interfaz
    web del reto.

    Una copia de referencia de esta versión original queda guardada en
    app.clean/app.py por si se necesita restaurar el reto.
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
    Acepta el host/IP a diagnosticar vía parámetro 'host' (o 'ip' como
    alias, para compatibilidad) tanto en POST (formulario web) como en
    GET/POST (JSON), y ejecuta un ping hacia él.
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
    output = os.popen("ping -c 1 " + host).read()

    # =========================================================================
    # [TODO DEFENSA]: SELECCIÓN DE ESTRATEGIA DE MITIGACIÓN
    # Comenta la llamada vulnerable y descomenta ÚNICAMENTE la opción que
    # resuelva la vulnerabilidad sin romper la funcionalidad legítima del servicio.
    #
    # --- OPCIÓN 1 ---
    # if ";" in host or "&&" in host:
    #     output = "Host invalido"
    # else:
    #     res = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True, timeout=3)
    #     output = res.stdout or res.stderr
    #
    # --- OPCIÓN 2 ---
    # if not host.isdigit():
    #     output = "Host invalido"
    # else:
    #     res = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True, timeout=3)
    #     output = res.stdout or res.stderr
    #
    # --- OPCIÓN 3 ---
    # if not re.match(r"^[a-zA-Z0-9.-]+$", host):
    #     output = "Host invalido"
    # else:
    #     res = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True, timeout=3)
    #     output = res.stdout or res.stderr
    # =========================================================================
    # --- FIN BLOQUE VULNERABLE -----------------------------------------

    if request.is_json:
        return {"host": host, "output": output}

    return render_template("index.html", output=output, host=host)


if __name__ == "__main__":
    # debug=True habilita recarga automática (hot-reload) para que los
    # cambios que el estudiante haga en app.py se reflejen sin reiniciar
    # manualmente el contenedor.
    app.run(host="0.0.0.0", port=5001, debug=True)
