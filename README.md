# Forja-Solver

Proyecto Django para métodos numéricos: Punto Fijo y Trazador Cúbico, con sistema de usuarios premium y gráficas interactivas.

## Requisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Django 4.2.x o 4.3.x
- MySQL Server (o MariaDB)
- phpMyAdmin (opcional, para administrar la base de datos gráficamente)

## Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone <URL-del-repo>
cd Forja-Solver
```

### 2. Crear y activar un entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

Si no existe `requirements.txt`, instala manualmente:

```bash
pip install django==4.2.*
pip install mysqlclient
pip install numexpr
pip install reportlab
```

### 4. Configurar la base de datos MySQL

- Crea una base de datos llamada `solver` usando phpMyAdmin o consola:

```sql
CREATE DATABASE solver CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

- Crea un usuario y dale permisos (opcional):

```sql
CREATE USER 'solveruser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON solver.* TO 'solveruser'@'localhost';
FLUSH PRIVILEGES;
```

- Edita `solver/settings.py` para que la sección DATABASES quede así:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'solver',
        'USER': '',  # o tu usuario
        'PASSWORD': '',  # tu contraseña
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Realizar migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear un superusuario (opcional, para admin)

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Abre tu navegador en http://127.0.0.1:8000/

---

## Uso de phpMyAdmin

- Instala phpMyAdmin y accede a http://localhost/phpmyadmin
- Ingresa con tu usuario y contraseña de MySQL
- Selecciona la base de datos `solver` para ver/modificar tablas y datos

---

## Notas adicionales

- Si agregas nuevas dependencias, actualiza `requirements.txt` con:
  ```bash
  pip freeze > requirements.txt
  ```
- Si tienes problemas con `mysqlclient`, instala las dependencias de compilación de MySQL (en Windows, instala MySQL y agrega sus binarios a PATH).
- El proyecto está preparado para Python 3.10+ y Django 4.2/4.3.

---

## Estructura principal

- `manage.py` — Comando principal de Django
- `solver/` — Configuración global del proyecto
- `calculadora/` — App principal (modelos, vistas, formularios)
- `static/` y `templates/` — Archivos estáticos y plantillas HTML

---

## Contacto y créditos

Ver sección de créditos en la app para información de los autores.
