#!/bin/bash
# Arranca Flask (puerto 5001, con recarga automática) en segundo plano
# y expone una terminal bash vía ttyd (puerto 7681) en primer plano,
# para que el estudiante pueda editar app.py en vivo y ver los cambios
# reflejados sin reiniciar el contenedor.

set -e

cd /app

# Lanza Flask en background. FLASK_DEBUG habilita el autoreloader.
export FLASK_APP=app.py
export FLASK_DEBUG=1
python3 app.py &

# ttyd en primer plano: terminal bash dentro de /app para el estudiante.
exec ttyd -p 7681 -W bash -c "cd /app && exec bash"
