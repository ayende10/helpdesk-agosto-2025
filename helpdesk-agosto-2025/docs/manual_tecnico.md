# Manual Técnico - Sistema Help Desk

## 1. Descripción de la arquitectura

El sistema Help Desk está compuesto por tres capas principales:

- **Front-End (Interfaz de Usuario)**
  - Plantillas HTML con Jinja2.
  - Estilos y componentes con Bootstrap 5.
  - Interactividad básica con jQuery y Chart.js para gráficos.

- **Back-End (Servidor de Aplicaciones)**
  - Implementado en Flask (Python).
  - Control de rutas, autenticación, roles y lógica de negocio.
  - Werkzeug para hashing de contraseñas.
  - Mensajes flash para retroalimentación al usuario.

- **Base de Datos (Persistencia)**
  - Motor: MariaDB/MySQL.
  - Conexión mediante PyMySQL.
  - Tres tablas principales:
    - `users`: gestión de cuentas y roles.
    - `tickets`: almacenamiento de tickets de soporte.
    - `ticket_comments`: comentarios asociados a cada ticket.

---

## 2. Diagrama ER

El diagrama entidad-relación se encuentra en la carpete de screenchots con el nombre DER.png



### 3.1 Crear base de datos
```sql

CREATE DATABASE helpdesk_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; 


### 3.2 Ejecutar script SQL
Ejecuta el script schema.sql incluido en la carpeta db/ para crear las tablas users, tickets y ticket_comments.

```sql

USE helpdesk_db;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('ADMIN', 'AGENT', 'USER') NOT NULL DEFAULT 'USER',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  status ENUM('OPEN', 'IN_PROGRESS', 'RESOLVED') NOT NULL DEFAULT 'OPEN',
  priority ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL DEFAULT 'MEDIUM',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by INT NOT NULL,
  assigned_to INT NULL,
  CONSTRAINT fk_tickets_created_by FOREIGN KEY (created_by) REFERENCES users(id),
  CONSTRAINT fk_tickets_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id)
);

CREATE TABLE ticket_comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  ticket_id INT NOT NULL,
  user_id INT NOT NULL,
  comment TEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_comments_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id),
  CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id)
);


### 3.3 Configurar .env

DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=helpdesk
SECRET_KEY=una_clave_secreta_segura


### 3.4 Instalar dependencias

pip install -r requirements.txt

### 3.5 Ejecutar el app.py

python app.py

La aplicacion estara disponible en http://127.0.0.1:50000

#### 4.  Descripción de rutas principales (Endpoints)

Las rutas se agrupan por funcionalidad: **Autenticación**, **Dashboard**, **Tickets**, **Comentarios** y **Usuarios**.

---

### 🔑 Autenticación
| Endpoint | Método | Rol requerido | Descripción |
|----------|--------|---------------|-------------|
| `/` | GET | Todos | Redirige a **Login** o **Dashboard** según sesión activa. |
| `/login` | GET / POST | Todos | Permite iniciar sesión con email y contraseña. |
| `/register` | GET / POST | Todos | Registro de nuevos usuarios (rol por defecto: **USER**). |
| `/logout` | GET | Autenticado | Cierra sesión y limpia datos de usuario. |

---

### 📊 Dashboard
| Endpoint | Método | Rol requerido | Descripción |
|----------|--------|---------------|-------------|
| `/dashboard` | GET | Autenticado | Muestra estadísticas generales del sistema. |

---

### 🎫 Tickets
| Endpoint | Método | Rol requerido | Descripción |
|----------|--------|---------------|-------------|
| `/tickets` | GET | Autenticado | Lista tickets según rol:<br>• **Admin**: todos<br>• **Agent**: asignados o sin asignar<br>• **User**: propios |
| `/tickets/new` | GET / POST | User / Agent / Admin | Crear un nuevo ticket con título, descripción y prioridad. |
| `/tickets/<ticket_id>` | GET | Autenticado | Ver detalle de un ticket y sus comentarios asociados. |
| `/tickets/<ticket_id>/update` | POST | Admin / Agent | Actualizar estado (OPEN, IN_PROGRESS, RESOLVED) y asignar agente. |

---

### 💬 Comentarios
| Endpoint | Método | Rol requerido | Descripción |
|----------|--------|---------------|-------------|
| `/tickets/<ticket_id>/comments` | POST | Autenticado | Añadir un comentario al ticket. |

---

### 👥 Usuarios
| Endpoint | Método | Rol requerido | Descripción |
|----------|--------|---------------|-------------|
| `/users` | GET | Admin | Listar todos los usuarios registrados. |
| `/users/<user_id>/role` | POST | Admin | Cambiar rol de usuarios(**USER**, **AGENT**, **ADMIN**). |

##### 5. Intento de mejora

Para este proyecto intente crear en el dashboard unos recuadros con los tipos de estados y cantidad de ticket que se actualizaran automaticamente sin necesidad de darle refresh a la pagina completa. 

##### 6. Link de Git




