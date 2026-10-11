#!/bin/bash
# Arranca Flask (puerto 5002, con recarga automática) en segundo plano
# y expone una terminal bash vía ttyd (puerto 7682) en primer plano,
# para que el estudiante pueda editar app.py en vivo y ver los cambios
# reflejados sin reiniciar el contenedor.
#
# Este script arranca como root (ver Dockerfile: ya no hay USER antes
# del ENTRYPOINT) únicamente para corregir la propiedad de /app, que
# en algunos hosts (p. ej. bind mounts de Docker Desktop en Windows)
# aparece como root sin importar el chown hecho en build time. Sin
# este arreglo, el usuario 'student' no podría ejecutar chmod sobre
# app.py desde unlock.py (chmod exige ser el propietario del archivo).
# Flask y ttyd se ejecutan como 'student' vía 'su', nunca como root.

set -e

chown -R student:student /app
chmod 444 /app/app.py

cd /app

export FLASK_APP=app.py
export FLASK_DEBUG=1

# Flask en background, como 'student'.
su -s /bin/bash student -c "cd /app && python3 app.py" &

# ttyd en primer plano, como 'student': terminal bash dentro de /app,
# mostrando primero un mensaje de bienvenida con las instrucciones de
# la fase defensiva (ver ttyd-welcome.sh).
exec su -s /bin/bash student -c "cd /app && exec ttyd -p 7682 -W /usr/local/bin/ttyd-welcome.sh"
