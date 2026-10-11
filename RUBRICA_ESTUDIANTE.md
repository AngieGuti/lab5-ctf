# Rúbrica de Sustentación — Lab5 CTF (15 minutos por grupo)

Este documento se puede compartir con los estudiantes **antes** de su
sustentación. No contiene flags, payloads ni soluciones — solo los
hitos que deben demostrar en vivo para cada nota.

## Tiempo de la sustentación

| Minuto | Fase |
|---|---|
| 0–5 | Fase Ofensiva: explotar la vulnerabilidad y obtener la flag. |
| 5–10 | Fase Defensiva: editar `app.py` en vivo (vía terminal web) y aplicar el parche. |
| 10–15 | Verificación en vivo (el evaluador prueba una variante del ataque) + 1 pregunta teórica sobre impacto/riesgo residual. |

## Escala de notas

La nota de cada reto es **únicamente** 0, 2.5 o 5.0 — no hay puntos
intermedios. Cada nivel exige cumplir **todo** lo del nivel anterior
más lo nuevo.

---

### Reto 1 — Command Injection (DMZ.10)

| Nota | Para obtenerla deben... |
|---|---|
| **0** | No logran que el servidor ejecute nada distinto a lo que la herramienta debería hacer (no obtienen la flag) en los primeros 5 minutos. |
| **2.5** | Logran que el servidor ejecute un comando adicional al esperado y obtienen la flag, **y** explican con sus palabras por qué su entrada logra "escapar" del comando original. |
| **5.0** | Además de lo anterior: editan `app.py` en vivo para que la entrada del usuario ya no pueda alterar el comando ejecutado. El parche debe seguir permitiendo el uso normal de la herramienta (un host válido debe seguir funcionando), resistir el mismo ataque que usaron **y** resistir una variante distinta que probará el evaluador en el momento. Deben también responder correctamente una pregunta teórica sobre el riesgo que queda si la solución no se hace bien. |

**Importante:** un parche que bloquee *solo* el ataque exacto que
usaron, pero que falle ante una variante ligeramente distinta, **no**
alcanza el 5.0 — se queda en 2.5. Tampoco alcanza el 5.0 un parche que
"arregle" el problema rompiendo el uso normal de la herramienta.

---

### Reto 2 — IDOR / Control de Acceso Roto

| Nota | Para obtenerla deben... |
|---|---|
| **0** | No logran ver información de un recurso que no les pertenece (no obtienen la flag) en los primeros 5 minutos. |
| **2.5** | Inician sesión con el usuario de prueba, logran ver el recurso de **otro** usuario cambiando un identificador en la petición, obtienen la flag, **y** explican con sus palabras por qué el sistema permite esto (pista: estar autenticado no es lo mismo que estar autorizado). |
| **5.0** | Además de lo anterior: editan `app.py` en vivo para agregar la verificación de propiedad del recurso faltante. Tras el parche, el acceso al recurso ajeno debe quedar bloqueado con el código de error correcto (prohibido / no autorizado), tanto en la interfaz web como en la vía alterna (API) si existe, **sin** romper el acceso al propio recurso del usuario. Deben también responder correctamente una pregunta teórica sobre el riesgo residual. |

**Importante:** un parche que bloquee el acceso en una sola de las
dos rutas del sistema (web y API) pero deje la otra abierta **no**
alcanza el 5.0. Tampoco alcanza el 5.0 un parche que bloquee también
el acceso legítimo del usuario a su propio recurso.

---

## Nota final

- Si la sustentación evalúa **un solo reto**, su nota final es
  directamente la nota de ese reto (0, 2.5 o 5.0).
- Si evalúa **ambos retos**, la nota final se calcula a partir del
  promedio de las dos notas de reto, según el criterio que el profesor
  confirme antes de la sustentación.
