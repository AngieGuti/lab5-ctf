# Reto 1 — Command Injection (DMZ.10 Diagnostic Tool)

## Contexto
Una herramienta interna de diagnóstico de red en la zona DMZ.10 permite
hacer "ping" a un host desde una interfaz web. El backend ejecuta el
comando del sistema operativo concatenando directamente la entrada del
usuario, sin validarla ni sanitizarla.

## Acceso
- **Aplicación web:** http://localhost:5001
- **Terminal (ttyd):** http://localhost:7681 (usuario `student`)

`app.py` arranca en modo **solo lectura** (`chmod 444`): no se puede
editar hasta demostrar que se obtuvo la flag (ver "Parte defensiva").

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
2. Ejecute el script de desbloqueo e ingrese la flag obtenida:

   ```bash
   python unlock.py
   ```

   Si la flag es correcta, el script:
   - Muestra un breve reporte de incidente (estilo CSIRT).
   - Habilita permisos de escritura sobre `app.py` (`chmod 664`).
   - Abre automáticamente `app.py` en `nano`.

3. Dentro de `nano`, localice el bloque marcado `[TODO DEFENSA]` y
   siga sus instrucciones:
   - Comentar la línea vulnerable (`os.popen(...)`).
   - Descomentar **únicamente** la opción correcta de las tres
     presentadas (A: lista negra — insuficiente; B: solo dígitos —
     demasiado restrictiva; C: lista blanca con regex — la correcta).
4. Guarde (`Ctrl+O`, Enter) y salga (`Ctrl+X`). Flask corre con
   recarga automática (`debug=True`), por lo que el cambio se refleja
   de inmediato sin reiniciar el contenedor.
5. Verifique que el mismo payload (`127.0.0.1; cat flag.txt`) ya no
   funciona y que un ping legítimo (`127.0.0.1`, `8.8.8.8`) sí responde
   con normalidad.

## Restauración
Para volver al estado inicial (vulnerable y bloqueado) de **todos**
los retos, desde la raíz del laboratorio ejecute:

```bash
./reset.sh
# o, de forma multiplataforma:
python reset.py
```

Esto restaura `app.py` y `unlock.py` desde `app.clean/` y vuelve a
dejar `app.py` en modo solo lectura (`chmod 444`) para el siguiente
grupo.
