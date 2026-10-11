"""
Sistema de Consulta de Reportes de Auditoría de Seguridad
-----------------------------------------------------------
Lab5 CTF - Reto 2: IDOR / Broken Access Control

⚠️ VERSION VULNERABLE (a propósito, para fines docentes) ⚠️

Este sistema permite a los usuarios autenticados consultar sus propios
reportes de auditoría. El problema es que el endpoint que devuelve un
reporte solo verifica que el usuario esté AUTENTICADO, pero nunca
verifica que el reporte solicitado le pertenezca (comparar
report['user_id'] contra session['user_id']). Esto es un Insecure
Direct Object Reference (IDOR) / Broken Access Control: cualquier
usuario autenticado puede leer el reporte de cualquier otro usuario
simplemente cambiando el parámetro `id`.

Usuarios de prueba:
    - admin   / admin_pwd_secret  (user_id = 1) -> dueño del reporte id=1 (confidencial, contiene la flag)
    - auditor / auditor123        (user_id = 2) -> dueño del reporte id=2

Objetivo del reto (ofensivo):
    1. Iniciar sesión como 'auditor' / 'auditor123'.
    2. Acceder a su propio reporte: /report?id=2
    3. Cambiar el parámetro a id=1 (el reporte del admin) y leer la flag,
       sin haber iniciado sesión como admin:
           /report?id=1
       o vía API:
           /api/report/1

Objetivo del reto (defensivo):
    Acceder a la terminal web en http://<host>:7682, abrir este archivo
    ('nano app.py' dentro de /app) y, en las rutas /report y
    /api/report/<id>, agregar la validación de autorización que falta
    en el bloque marcado [TODO DEFENSA] más abajo.

    Una copia de referencia de esta versión vulnerable original queda
    guardada en app.clean/app.py por si se necesita restaurar el reto.
"""

import os
import sqlite3

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.sqlite")

app = Flask(__name__)
app.secret_key = "lab5-ctf-challenge2-dev-secret-key"  # Uso exclusivo de laboratorio


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("report", id=session["user_id"]))
    return redirect(url_for("login"))


# ------------------------------------------------------------------
# /login y /logout funcionan de forma completamente independiente:
# no dependen de (ni son bloqueadas por) ninguna verificación de
# autorización. Cualquiera puede llegar a /login sin sesión previa,
# y /logout siempre limpia la sesión sin condiciones adicionales.
# ------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()

        if user is not None:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            # Cada usuario tiene un reporte propio cuyo id coincide con su user_id
            return redirect(url_for("report", id=user["id"]))

        error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/report")
def report():
    """
    Endpoint vulnerable a IDOR.

    Solo exige que exista una sesión activa (usuario autenticado),
    pero NUNCA verifica que el reporte solicitado (`id`) pertenezca al
    usuario autenticado. Esto permite a cualquier usuario leer el
    reporte de cualquier otro usuario cambiando el parámetro `id`.
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    report_id = request.args.get("id", session["user_id"])

    conn = get_db()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if row is None:
        return "Reporte no encontrado", 404

    # ========================================================
    # [TODO DEFENSA]: CONTROL DE ACCESO (IDOR)
    # Agrega aquí la validación: si el reporte no pertenece al
    # usuario autenticado, retorna abort(403).
    # Pista: Compara row["user_id"] con session.get("user_id")
    # ========================================================

    return render_template("report.html", report=row, username=session["username"])


@app.route("/api/report/<int:report_id>")
def api_report(report_id):
    """
    Variante API del mismo endpoint vulnerable, devuelve JSON.
    Igual que /report, no valida la propiedad del reporte.
    """
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    conn = get_db()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Reporte no encontrado"}), 404

    # ========================================================
    # [TODO DEFENSA]: CONTROL DE ACCESO (IDOR)
    # Agrega aquí la validación: si el reporte no pertenece al
    # usuario autenticado, retorna abort(403).
    # Pista: Compara row["user_id"] con session.get("user_id")
    # ========================================================

    return jsonify({
        "id": row["id"],
        "user_id": row["user_id"],
        "title": row["title"],
        "content": row["content"],
    })


if __name__ == "__main__":
    # debug=True habilita recarga automática (hot-reload) para que los
    # cambios que el estudiante haga en app.py se reflejen sin reiniciar
    # manualmente el contenedor.
    app.run(host="0.0.0.0", port=5002, debug=True)
