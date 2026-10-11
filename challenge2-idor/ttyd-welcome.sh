#!/bin/bash
# Mensaje de bienvenida mostrado al abrir la terminal web (ttyd) del
# Reto 2, antes de entregar el control al shell interactivo.

cat <<'EOF'
========================================================================
 Lab5 CTF - Terminal de Edición · Reto 2: IDOR / Broken Access Control
========================================================================
 Fase Defensiva: Para modificar el código, ejecuta:

     python unlock.py

 e ingresa la flag obtenida en la Fase Ofensiva.
========================================================================
EOF

cd /app
exec bash
