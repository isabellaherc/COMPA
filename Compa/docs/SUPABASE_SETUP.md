# SUPABASE_SETUP.md -- Compa

> **Duracion estimada**: 15 minutos | **Nivel**: Principiante absoluto
> **Objetivo**: Ir de cero a una base de datos Supabase funcional conectada a n8n
> **Hackathon**: Cursor Buildathon -- 4 Julio 2026 -- UFG

---

## Indice

1. [Crear cuenta en Supabase](#1-crear-cuenta-en-supabase)
2. [Crear proyecto](#2-crear-proyecto)
3. [Esperar a que el proyecto se provisione](#3-esperar-a-que-el-proyecto-se-provisione)
4. [Obtener credenciales](#4-obtener-credenciales)
5. [Abrir SQL Editor](#5-abrir-sql-editor)
6. [Pegar y ejecutar el schema SQL](#6-pegar-y-ejecutar-el-schema-sql)
7. [Verificar los datos](#7-verificar-los-datos)
8. [Obtener connection string para n8n](#8-obtener-connection-string-para-n8n)
9. [Configurar n8n Postgres node](#9-configurar-n8n-postgres-node)
10. [Probar conexion desde n8n](#10-probar-conexion-desde-n8n)
11. [Errores comunes y soluciones](#11-errores-comunes-y-soluciones)
12. [Checklist final](#12-checklist-final)

---

## 1. Crear cuenta en Supabase

1. Abri tu navegador e ingresa a **https://app.supabase.com**
2. Hace clic en **"Start your project"** o **"Sign Up"**
3. Podes registrarte con:
   - **GitHub** (recomendado, un solo clic)
   - **GitLab**
   - **Email + contrasena**

![Pantalla de login de Supabase] Aparece un formulario centrado con botones de GitHub, GitLab y email. Fondo blanco con el logo de Supabase (un triangulo verde formado por 3 puntos) arriba.

4. Si usas GitHub: autoriza la aplicacion Supabase en la ventana de GitHub que se abre.
5. Completa tu nombre y empresa (opcional, podes poner "Compa Buildathon").
6. Marca los terminos y condiciones.
7. Vas a caer al **Dashboard** principal.

---

## 2. Crear proyecto

Ya dentro del dashboard:

1. Hace clic en **"New project"** (boton verde-azulado, esquina superior derecha).

![Dashboard de Supabase] Panel con sidebar izquierdo (Home, SQL Editor, Database, Authentication, Storage, etc.). Centro: lista de proyectos o boton "New project".

2. Completa el formulario:

| Campo | Valor |
|---|---|
| **Name** | `compa` |
| **Database Password** | Hace clic en **"Generate a secure password"** y copiala en tu `.env` o en un bloc de notas. Tambien podes escribir una manualmente (minimo 8 caracteres, mayuscula, minuscula, numero). |
| **Region** | `US East (North Virginia)` -- seleccionala del dropdown |
| **Pricing Plan**| `Free Tier` (default, viene preseleccionado) |

3. Importante: anota el **password** en un lugar seguro. Si lo perdes, podes rescatarlo despues (ver [Errores comunes](#11-errores-comunes-y-soluciones)).

4. Hace clic en **"Create new project"**.

---

## 3. Esperar a que el proyecto se provisione

Supabase tarda entre **1 y 3 minutos** en provisionar tu base de datos.

- La pantalla muestra una barra de progreso con el mensaje `"Your project is being created... Your database is being set up..."`
- Podes ver 3 estados:
  1. **Initializing** -- creando los recursos de infraestructura
  2. **Setting up database** -- configurando PostgreSQL
  3. **Finalizing** -- activando el dashboard

![Pantalla de provisioning] Fondo oscuro con un spinner/barra de progreso animada verde. Texto: "Your project is being created..." y algunos datos tecnicos (region, plan, etc.).

**No cierres la ventana.** Cuando termina, el boton de la barra de progreso cambia a **"Go to project"** o automaticamente te redirige al dashboard del proyecto.

---

## 4. Obtener credenciales

Una vez que el proyecto esta listo, estas en la pagina del proyecto. Necesitas 3 cosas:

1. **Project URL** (tambien llamado `SUPABASE_URL`)
2. **anon key** (`SUPABASE_ANON_KEY`)
3. **service_role key** (`SUPABASE_SERVICE_ROLE_KEY`)

### Como obtenerlas

1. En el sidebar izquierdo, hace clic en **Project Settings** (icono de engranaje, abajo del todo).

![Project Settings] Sidebar izquierdo con "Project Settings" resaltado. Abre una pagina con pestanas: General, Database, API, Authentication, etc.

2. En la pestana **General**, busca la seccion **"Project Configuration"**. Ahi esta el **Project URL** (algo como `https://xxxxxxxxxxxxxxxxxxxx.supabase.co`). Copialo.

3. Ahora hace clic en la pestana **API** (dentro de Project Settings).

4. En la seccion **"Project API keys"** vas a ver dos llaves:

   - **anon public** -- empieza con `eyJ...` (es un JWT). Esta es la `SUPABASE_ANON_KEY`.
   - **service_role** -- empieza con `eyJ...`. Esta es la `SUPABASE_SERVICE_ROLE_KEY`.

5. Copia las 3 credenciales a tu archivo `.env`:

```
SUPABASE_URL=https://xxxxxxxxxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

> **IMPORTANTE**: La `service_role key` tiene permisos totales. Nunca la expongas en frontend o repos publicos. Para n8n (backend), es la que tenes que usar.

---

## 5. Abrir SQL Editor

1. En el sidebar izquierdo, hace clic en **SQL Editor** (icono de `</>`).

![SQL Editor vacio] Pagina con un editor de texto grande en el centro, un boton "New query" arriba a la derecha, y posiblemente algunas queries de ejemplo precargadas ("Getting started" cards).

2. Hace clic en **"New query"** (boton verde, esquina superior derecha). Se abre una pestana nueva con un editor SQL vacio.

---

## 6. Pegar y ejecutar el schema SQL

Nuestro archivo de schema esta en: `C:\Users\joshb\Documents\Compa\supabase-schema.sql`

**IMPORTANTE**: Este archivo contiene tanto las sentencias `CREATE TABLE` (schema) como las `INSERT INTO` (seed data) en un solo archivo. Podes ejecutarlo completo de una sola vez.

### Opcion A: Copiar el archivo completo (recomendado)

1. Abri `supabase-schema.sql` en tu editor de texto favorito (VS Code, Bloc de Notas, etc.).
2. Selecciona TODO el contenido (Ctrl+E / Ctrl+A, Ctrl+C).
3. En el SQL Editor de Supabase, pega el contenido (Ctrl+V).
4. Hace clic en **"Run"** (boton azul, esquina superior derecha del editor).

### Opcion B: Desde el disco local

1. En el SQL Editor, hace clic en el icono de **"Insert from file"** o arrastra el archivo `supabase-schema.sql` directamente al editor.

### Que va a pasar

El SQL Editor va a ejecutar el script completo que:

1. Crea la tabla `productores` con sus indices y constraints
2. Crea la tabla `oportunidades` con sus indices y constraints
3. Crea la tabla `proveedores` con sus indices y constraints
4. Crea la tabla `decisiones` con sus indices y constraints
5. Habilita Row Level Security (RLS) en todas las tablas
6. Crea politicas permisivas para el demo
7. Inserta 5 filas en `productores`
8. Inserta 5 filas en `oportunidades`
9. Inserta 5 filas en `proveedores`
10. Inserta 5 filas en `decisiones`
11. Crea la funcion `matching_oportunidades()` para matching por rubro

### Que ver

- Si todo sale bien: ves un mensaje **"Success. No rows returned"** (las CREATE TABLE no devuelven filas) y luego **"Success. 5 rows returned"** (los INSERT devuelven las filas insertadas).
- Si aparecen errores en rojo, anota el mensaje exacto. Los mas comunes estan en la seccion [Errores comunes](#11-errores-comunes-y-soluciones).

![SQL Editor con exito] Editor de texto con SQL pegado. Abajo aparece el panel de resultados con mensajes verdes de "Success" y las filas insertadas.

---

## 7. Verificar los datos

Para confirmar que todo se creo correctamente, ejecuta estas consultas en el SQL Editor (podes escribir una nueva query o reemplazar el contenido):

```sql
SELECT 'productores' AS tabla, COUNT(*) AS total FROM productores
UNION ALL
SELECT 'oportunidades', COUNT(*) FROM oportunidades
UNION ALL
SELECT 'proveedores', COUNT(*) FROM proveedores
UNION ALL
SELECT 'decisiones', COUNT(*) FROM decisiones;
```

Hace clic en **Run**. Deberias ver:

| tabla | total |
|---|---|
| productores | 5 |
| oportunidades | 5 |
| proveedores | 5 |
| decisiones | 5 |

Si algun count es 0, significa que esa tabla no se creo o los INSERT fallaron. Revisa la seccion [Errores comunes](#11-errores-comunes-y-soluciones).

### Query de matching (opcional pero util para el demo)

Para ver como funciona el matching de oportunidades para Vilma:

```sql
SELECT * FROM matching_oportunidades('a1000000-0000-0000-0000-000000000001');
```

Resultado esperado: 3 oportunidades con scores de 100, 70 y 70.

---

## 8. Obtener connection string para n8n

n8n se conecta a Supabase usando el **Postgres node** con una connection string (URI).

### Paso a paso

1. En el sidebar izquierdo, hace clic en **Project Settings** (engranaje).
2. Hace clic en la pestana **Database**.
3. En la seccion **"Connection string"**, busca la URI.

![Pantalla Database settings] Muestra la informacion de conexion: Host, Port, Database name, y un dropdown para seleccionar el tipo de connection string (URI, psql, golang, etc.).

4. En el dropdown, selecciona **"URI"**.
5. Copia la URI que se muestra. Tiene este formato:

```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxxxxxxxxx.supabase.co:5432/postgres
```

6. Reemplaza `[YOUR-PASSWORD]` con la contrasena que generaste en el paso 2.

La connection string final queda asi (con tu password real):

```
postgresql://postgres:TuPasswordSeguro123@db.xxxxxxxxxxxxxxxxxxxx.supabase.co:5432/postgres
```

> **Nota**: El puerto siempre es `5432`. El host suele ser `db.XXXXXXXXXXXXX.supabase.co`.

---

## 9. Configurar n8n Postgres node

1. Abri tu proyecto de **n8n Cloud** en `https://app.n8n.cloud`.
2. Abri el workflow donde queres usar Supabase (o crea uno nuevo).
3. Arrastra un nodo **Postgres** desde la paleta de nodos al canvas.

![n8n canvas] Grid gris del canvas de n8n con un nodo Postgres recien colocado, con el borde naranja indicando que no esta configurado.

4. Hace doble clic en el nodo para abrir la configuracion.
5. En el campo **"Connection"**, selecciona **"New"**.
6. En el campo **"Connection String"**, pega la URI completa del paso anterior.

![Configuracion Postgres node en n8n] Panel lateral derecho con campos: "Connection" (dropdown), "Connection String" (campo de texto), "Query" (campo de texto para SQL).

7. Deja los otros campos por defecto.
8. Hace clic en **"Save"** (esquina superior derecha del panel).

---

## 10. Probar conexion desde n8n

1. Con el nodo Postgres seleccionado, anda a la pestana **"Query"**.
2. Escribe una consulta simple:

```sql
SELECT * FROM productores;
```

3. En la barra superior, hace clic en el boton **"Execute Node"** (icono de play, solo ejecuta este nodo).
4. Si la conexion funciona, vas a ver el panel de **Output** con los datos de los productores (5 filas).

![n8n Output exitoso] Panel lateral derecho con pestana Output. Muestra un array JSON con las 5 filas de la tabla productores. Cada fila con sus campos: id, nombre, rubro, ubicacion, etc.

5. Si ves los datos, **felicidades -- la conexion Supabase + n8n funciona**.

6. Como paso final, guarda la conexion como un **Credential** reutilizable:
   - En el panel del nodo Postgres, hace clic en el campo "Connection" y selecciona "Create New Credential".
   - Ponle nombre: **`Compa Supabase`**.
   - Pega la connection string.
   - Guarda.

Para workflows futuros, solo seleccionas la credencial "Compa Supabase" y no tenes que pegar la URI otra vez.

---

## 11. Errores comunes y soluciones

### "Password reset" -- Donde encontrar la contrasena

**Problema**: Perdiste la contrasena que generaste al crear el proyecto y no podes conectarte.

**Solucion**: Supabase no muestra la contrasena original, pero podes resetearla:

1. En el sidebar, anda a **Project Settings** > **Database**.
2. En la seccion **"Database Configuration"**, busca **"Reset Database Password"** o simplemente **"Database Password"**.
3. Hace clic en **"Reset password"**.
4. Ingresa una nueva contrasena (o genera una).
5. Copiala inmediatamente en tu `.env`.
6. Actualiza la connection string en tu credential de n8n con la nueva contrasena.
7. Ejecuta el nodo Postgres de nuevo para verificar.

![Reset password en Supabase] Seccion Database Settings con un campo "Database Password" y un boton "Reset password" al lado. Hay una advertencia de que los servicios que usen esta contrasena van a fallar hasta que se actualice.

### "Connection refused" -- IP allowlist o connection pooling

**Problema**: n8n no puede conectar a Supabase. Error tipico: `ECONNREFUSED` o `timeout`.

**Causa 1 -- IP Allowlist**: Supabase Free Tier viene con proteccion por IP. Si la IP de n8n Cloud no esta en la lista de permitidas, la conexion es rechazada.

**Solucion**:
1. En Supabase, anda a **Project Settings** > **Database**.
2. En la seccion **"IP Allow List"**, revisa si hay IPs configuradas.
3. Si n8n Cloud no conecta, podes desactivar temporalmente el IP Allowlist (dejarlo vacio) durante el hackathon.
4. O usa **Connection Pooling** (mas abajo).

**Causa 2 -- Connection Pooling**: Supabase tiene un `pgbouncer` que maneja conexiones. A veces es necesario conectarse a traves del pooler en lugar de directo.

**Solucion -- Usar connection pooling**:
1. En la misma pestana **Database**, busca **"Connection Pooling"**.
2. Activa el toggle **"Use connection pooling"**.
3. La connection string cambia a algo como:
   ```
   postgresql://postgres:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
   ```
4. Nota el puerto: **6543** (no 5432) cuando usas pooler.
5. Copia esta nueva URI y usala en n8n.

### "Relation does not exist" -- Ejecutar schema.sql primero

**Problema**: Al consultar `SELECT * FROM productores`, recibis:

```
relation "productores" does not exist
```

**Causa**: La tabla no fue creada. Esto pasa si:
- No ejecutaste el schema.sql.
- Lo ejecutaste pero en el proyecto equivocado.
- Lo ejecutaste pero hubo un error silencioso.

**Solucion**:
1. Abri el SQL Editor de nuevo.
2. Ejecuta SOLO el CREATE TABLE (o todo el `supabase-schema.sql`).
3. Verifica con `SELECT * FROM information_schema.tables WHERE table_schema = 'public';`
4. Si la tabla aparece pero sigue dando error, revisa que el schema sea `public` (por defecto). Si creaste la tabla en otro schema, usa `SET search_path TO tu_schema;`.

### "Password authentication failed for user 'postgres'"

**Causa**: La contrasena en la connection string no coincide con la de la base de datos.

**Solucion**:
1. Resetea la contrasena (ver "Password reset" arriba).
2. Actualiza la URI en n8n.

### "Cannot read properties of undefined (reading 'json')" en n8n

**Causa**: El nodo Postgres devolvio un resultado vacio o en un formato que el nodo siguiente no espera.

**Solucion**:
1. Ejecuta el nodo Postgres solo para verificar que devuelve datos.
2. Si devuelve datos, revisa que el nodo siguiente use `$json` correctamente.
3. En el Code Node que sigue al Postgres, usa:
   ```javascript
   const data = $input.first().json;
   // o para multiples filas:
   const rows = $input.all().map(item => item.json);
   ```

### Conexion funciona en Supabase SQL Editor pero no en n8n

**Causa**: La IP de n8n Cloud esta bloqueada por Supabase.

**Solucion**: Connection pooling (ver arriba) resuelve esto porque el pooler acepta conexiones desde cualquier IP.

---

## 12. Checklist final

Marca estos items cuando esten completos:

### Cuenta y proyecto
- [ ] Cuenta en app.supabase.com creada
- [ ] Proyecto `compa` creado (region US East)
- [ ] Password guardado en `.env`
- [ ] Project URL copiado: `https://XXXXX.supabase.co`

### Schema y datos
- [ ] `supabase-schema.sql` ejecutado sin errores
- [ ] `SELECT COUNT(*)` devuelve 5, 5, 5, 5

### Credenciales
- [ ] `SUPABASE_URL` en `.env`
- [ ] `SUPABASE_ANON_KEY` en `.env`
- [ ] `SUPABASE_SERVICE_ROLE_KEY` en `.env`

### n8n
- [ ] Connection string armada: `postgresql://postgres:...`
- [ ] n8n Postgres node configurado
- [ ] Credential `Compa Supabase` creada y guardada
- [ ] `SELECT * FROM productores` ejecuta exitosamente desde n8n
- [ ] `SELECT * FROM matching_oportunidades(...)` devuelve resultados

---

## Apendice: Resumen de conexion para n8n

| Item | Donde encontrarlo |
|---|---|
| Project URL | Project Settings > General > Project URL |
| Anon key | Project Settings > API > anon public |
| Service role key | Project Settings > API > service_role (secret) |
| Connection string (directa) | Project Settings > Database > Connection string > URI |
| Connection string (pooler) | Project Settings > Database > Connection Pooling |
| Reset password | Project Settings > Database > Reset Database Password |
| SQL Editor | Sidebar > SQL Editor > New query |
| IP Allowlist | Project Settings > Database > IP Allow List |

---

## Apendice: Variables de entorno para `.env`

```
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# n8n connection string (POSTGRES)
PG_CONNECTION_STRING=postgresql://postgres:TuPasswordSeguro123@db.xxxxxxxxxxxxxxxxxxxx.supabase.co:5432/postgres

# Opcional: con connection pooling
# PG_CONNECTION_STRING=postgresql://postgres:TuPasswordSeguro123@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1
```

---

*Documento generado para Compa Buildathon -- 4 Julio 2026*
*Archivo: `C:\Users\joshb\Documents\Compa\docs\SUPABASE_SETUP.md`*
