#!/bin/bash
# Mensaje de bienvenida mostrado al abrir la terminal web (ttyd) del
# Reto 1, antes de entregar el control al shell interactivo.

cat <<'EOF'
========================================================================
 Lab5 CTF - Terminal de Edición · Reto 1: Command Injection (DMZ.10)
========================================================================
 Fase Defensiva: Para modificar el código, ejecuta:

     python unlock.py

 e ingresa la flag obtenida en la Fase Ofensiva. Obtendrás una flag
 defensiva para editar app.py con nano.
========================================================================
EOF

cd /app
exec bash
