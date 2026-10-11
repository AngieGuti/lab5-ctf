#!/bin/bash
# Arranca Flask (puerto 5002, con recarga automática) en segundo plano
# y expone una terminal bash vía ttyd (puerto 7682) en primer plano,
# para que el estudiante pueda editar app.py en vivo y ver los cambios
# reflejados sin reiniciar el contenedor.

set -e

cd /app

export FLASK_APP=app.py
export FLASK_DEBUG=1
python3 app.py &

exec ttyd -p 7682 -W bash -c "cd /app && exec bash"
