# Resumen técnico — Lab5 CTF (para revisión externa)

## Objetivo del proyecto
Entorno Docker para sustentaciones prácticas de 15 minutos por grupo,
en un curso universitario de seguridad (CIBER). Cada grupo debe:
1. Explotar una vulnerabilidad (fase ofensiva).
2. Parchearla en vivo editando el código desde una terminal web
   embebida en el propio contenedor (fase defensiva).
3. Demostrar que el parche resiste una variante del ataque y responder
   una pregunta teórica (verificación).

Hay dos retos independientes, cada uno en su propio contenedor Docker,
ambos orquestados por un único `docker-compose.yml` en la raíz.

## Estructura del repositorio

```
lab5-ctf/
├── docker-compose.yml
├── reset.sh
├── EVALUATION_GUIDE.md        # confidencial: flags, payloads, parches, rúbrica 0/2.5/5
├── RUBRICA_ESTUDIANTE.md      # público: mismos hitos, sin flags/soluciones
├── README.md
├── challenge1-injection/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── README.md
│   ├── app/                   # carpeta activa, montada como volumen en el contenedor
│   │   ├── app.py             # versión VULNERABLE (editable en vivo por el estudiante)
│   │   ├── flag.txt
│   │   └── templates/index.html
│   └── app.clean/
│       └── app.py             # copia de respaldo para reset.sh
└── challenge2-idor/
    ├── Dockerfile
    ├── entrypoint.sh
    ├── README.md
    ├── app/
    │   ├── app.py             # versión VULNERABLE (editable en vivo)
    │   ├── database.sqlite    # usuarios + reportes precargados
    │   ├── templates/login.html
    │   ├── templates/report.html
    │   └── static/            # vacío, solo .gitkeep
    └── app.clean/
        ├── app.py             # backup para reset.sh
        └── database.sqlite    # backup para reset.sh
```

## Infraestructura común (ambos retos)

- **Base de imagen:** `python:3.11-slim`.
- **Dependencias:** Flask (pip) + `ttyd` (binario estático descargado
  desde GitHub releases v1.7.4, arquitectura detectada vía
  `dpkg --print-architecture`) + utilidades (`bash`, `curl`, `nano`,
  `vim`, `procps`; reto 1 además `iputils-ping`, reto 2 además
  `sqlite3`).
- **Usuario de ejecución:** `student` (no root), creado con
  `useradd -ms /bin/bash student`, con permisos de escritura sobre
  `/app`.
- **Arranque (`entrypoint.sh`):** lanza `python3 app.py &` (Flask en
  modo `debug=True`, con autoreload) en segundo plano, y en primer
  plano expone `ttyd -p <puerto> -W bash -c "cd /app && exec bash"` —
  una terminal interactiva real dentro del contenedor, accesible desde
  el navegador.
- **Volúmenes:** `docker-compose.yml` monta `./challengeX/app:/app`
  como bind mount. Esto significa que:
  - Los cambios que el estudiante hace en `/app/app.py` desde la
    terminal ttyd se escriben directamente en el host.
  - El autoreload de Flask (`debug=True`) detecta el cambio y recarga
    la app sin reiniciar el contenedor.
  - `reset.sh` (que corre en el host) puede restaurar el estado
    original simplemente sobrescribiendo esos archivos — no hace falta
    reconstruir ni reiniciar los contenedores.
- **Puertos expuestos:**
  | Reto | App Flask | Terminal ttyd |
  |---|---|---|
  | Reto 1 (`challenge1-injection`) | `5001` | `7681` |
  | Reto 2 (`challenge2-idor`) | `5002` | `7682` |

## `docker-compose.yml`
Dos servicios (`challenge1-injection`, `challenge2-idor`), cada uno con
`build.context` a su carpeta, `container_name` fijo (`ctf-challenge1-injection`,
`ctf-challenge2-idor`), mapeo de puertos 1:1, volumen bind mount de su
`app/`, y `restart: unless-stopped`.

## `reset.sh`
Script Bash (ejecutable) en la raíz. Hace exactamente:
```bash
cp challenge1-injection/app.clean/app.py challenge1-injection/app/app.py
cp challenge2-idor/app.clean/*          challenge2-idor/app/
echo "[+] Entorno reiniciado con éxito para el siguiente grupo"
```
No reconstruye ni reinicia contenedores (no hace falta, por los
volúmenes + autoreload descritos arriba). Pensado para correr entre
cada grupo de sustentación.

---

## Reto 1 — Command Injection ("DMZ.10 Diagnostic Tool")

**Escenario:** herramienta interna de diagnóstico de red que ejecuta
`ping` hacia un host indicado por el usuario.

**Backend (`app/app.py`):**
- Flask, un solo archivo, sin base de datos.
- `GET /` → formulario HTML (`templates/index.html`).
- `POST/GET /diagnostic` → acepta `host` (o `ip`) vía JSON o
  form-urlencoded. Construye el comando así:
  ```python
  command = "ping -c 1 " + host
  output = os.popen(command).read()
  ```
  Sin ninguna validación ni sanitización → inyección de comandos del
  sistema operativo clásica (OS Command Injection).
- Devuelve el `output` crudo, tanto en la plantilla HTML como en JSON.

**Explotación esperada:**
```
127.0.0.1; cat flag.txt
```
(o `&&`, `|`) → el servidor ejecuta el ping **y** el comando inyectado,
revelando `challenge1-injection/app/flag.txt`:
```
FLAG{cmd_1nj3ct10n_dmz_byp4ss}
```

**Parche esperado (defensivo):** sustituir el bloque vulnerable por
`subprocess.run(["ping", "-c", "1", host], ...)` (lista de argumentos,
nunca shell) + validación de entrada (`ipaddress` o regex) antes de
ejecutar.

**Ya validado en pruebas reales (ver sección "Estado de pruebas" abajo):**
ping legítimo, inyección vía JSON, inyección vía formulario web,
reset.sh, autoreload tras editar en vivo.

---

## Reto 2 — IDOR / Broken Access Control ("Sistema de Reportes de Auditoría")

**Escenario:** sistema de consulta de reportes de auditoría de
seguridad, con login y sesiones.

**Backend (`app/app.py`):**
- Flask + `sqlite3` + `session` (cookie firmada con `app.secret_key`
  fijo, uso exclusivo de laboratorio).
- Base de datos `database.sqlite` con dos tablas:
  - `users(id, username, password)` — passwords en texto plano
    (intencional, foco pedagógico es IDOR, no hashing):
    - `admin` / `admin_pwd_secret` → `id=1`
    - `auditor` / `auditor123` → `id=2`
  - `reports(id, user_id, title, content)`:
    - `id=1`, `user_id=1` (admin) → contenido confidencial con la flag
      `FLAG{1d0r_br0k3n_4cc3ss_c0ntr0l}`
    - `id=2`, `user_id=2` (auditor) → reporte normal, sin flag
- Rutas:
  - `GET/POST /login` → valida contra la tabla `users`, guarda
    `session["user_id"]` / `session["username"]`, redirige a
    `/report?id=<propio id>`.
  - `GET /logout` → limpia sesión.
  - `GET /report` → requiere sesión activa (`if "user_id" not in
    session: redirect(login)`), pero **nunca compara**
    `report["user_id"]` contra `session["user_id"]`. Solo hace
    `SELECT * FROM reports WHERE id = ?` con el `id` que venga por
    query string.
  - `GET /api/report/<int:id>` → misma falla, variante JSON.

**Explotación esperada:** login como `auditor`, cambiar la URL de
`/report?id=2` (su reporte) a `/report?id=1` (reporte del admin) → se
muestra el contenido confidencial y la flag, sin haber iniciado sesión
como admin. Misma falla reproducible vía `/api/report/1` con la cookie
de `auditor`.

**Parche esperado (defensivo):** agregar, en ambas rutas, después de
obtener el `row`:
```python
if row["user_id"] != session.get("user_id"):
    return abort(403)
```

**Ya validado en pruebas reales:** login correcto/incorrecto, acceso a
reporte propio, IDOR vía web y vía API, bloqueo de acceso sin sesión
(redirect 302), escritura en vivo desde ttyd reflejada en el host,
reset.sh.

---

## Documentos de evaluación

- **`EVALUATION_GUIDE.md`** (confidencial, NO entregar a estudiantes):
  distribución de tiempo (0-5 ofensiva / 5-10 defensiva / 10-15
  verificación + teoría), cheatsheet completo de cada reto (pistas,
  payloads, código antes/después del parche, comandos de verificación),
  rúbrica de calificación **discreta** 0 / 2.5 / 5.0 por reto (sin
  puntos intermedios), tabla de combinación para nota final si se
  evalúan ambos retos, y banco de preguntas teóricas sobre impacto y
  riesgo residual.
- **`RUBRICA_ESTUDIANTE.md`** (público, se puede repartir antes de la
  sustentación): mismos tres niveles de nota (0 / 2.5 / 5.0) por reto,
  descritos en términos observables (qué deben lograr y demostrar),
  **sin** revelar flags, payloads ni el código del parche.

Regla de calificación clave: 2.5 = fase ofensiva completa (flag +
explicación del mecanismo); 5.0 = además fase defensiva completa
(parche robusto ante variante, sin romper funcionalidad legítima) +
verificación + pregunta teórica correcta. No hay valores intermedios.

## Estado de pruebas realizadas en esta sesión

Con Docker Desktop corriendo, se validó explícitamente (vía `docker
compose build/up` + `curl` + `docker exec`):

1. Build exitoso de ambas imágenes.
2. Ambos contenedores corren simultáneamente con sus puertos mapeados.
3. Reto 1: ping legítimo responde bien; inyección vía JSON y vía
   formulario web filtran la flag correcta.
4. Reto 2: login correcto redirige al reporte propio; acceso sin
   sesión redirige (302) a login; credenciales incorrectas muestran
   error; IDOR vía `/report?id=1` y `/api/report/1` filtran la flag
   correcta estando autenticado como `auditor`.
5. Usuario `student` dentro de ambos contenedores puede escribir en
   `/app/app.py` (verificado con una escritura de prueba), confirmando
   que la edición en vivo desde ttyd es viable.
6. `ttyd` responde HTTP 200 en ambos puertos (7681 y 7682).
7. `reset.sh` restaura correctamente ambos `app.py` tras una
   modificación simulada, imprime el mensaje exacto esperado, y
   ambas vulnerabilidades siguen explotables inmediatamente después
   del reset (sin rebuild/restart, gracias a volúmenes + autoreload).

**Lo que NO se ha probado explícitamente en esta sesión:**
- El flujo completo de "editar el parche defensivo real desde ttyd vía
  navegador" (solo se verificó que la escritura de archivos funciona y
  que el autoreload de Flask está habilitado; no se aplicó el parche
  completo del cheatsheet y se re-testeó la mitigación end-to-end).
- El comportamiento de `/api/report/<id>` y `/report` tras aplicar el
  parche de autorización (403 esperado) — está documentado pero no
  ejecutado contra código ya parchado.
- Pruebas de concurrencia / múltiples grupos usando el laboratorio al
  mismo tiempo (el diseño asume un solo grupo activo por contenedor a
  la vez, reiniciado con `reset.sh` entre grupos).
- Comportamiento en el entorno real donde se hará la sustentación
  (esta sesión usó Docker Desktop en Windows vía Git Bash; no se ha
  probado en Linux nativo ni en la máquina donde efectivamente se
  sustentará).
- Seguridad del propio laboratorio frente a un estudiante "travieso"
  que intente escapar del contenedor, atacar el host, o usar la
  terminal ttyd para algo distinto al ejercicio (no es un objetivo de
  diseño declarado, pero vale la pena que el revisor lo señale si lo
  considera relevante dado que ttyd da shell real con acceso a
  internet dentro del contenedor).

## Preguntas abiertas que el revisor podría ayudar a resolver
1. ¿La rúbrica de nota final combinada (promedio de los dos retos,
   con el caso ambiguo 2.5+5.0=3.75) necesita un criterio de redondeo
   definitivo antes de usarse en producción?
2. ¿Vale la pena fijar versiones exactas en `pip install flask` (sin
   pin) para reproducibilidad entre builds futuros?
3. ¿El `app.secret_key` fijo en el Reto 2 y las contraseñas en texto
   plano en SQLite son aceptables dado que el foco pedagógico es IDOR,
   o se prefiere endurecerlos igualmente por buenas prácticas?
4. ¿ttyd con `-W` (escritura habilitada) y sin autenticación adicional
   es aceptable para el contexto de aula, o se requiere algún control
   de acceso extra (ej. contraseña de ttyd) si el laboratorio se expone
   más allá de `localhost`?
