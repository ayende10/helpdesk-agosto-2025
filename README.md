# Help Desk Web App

## 📌 Descripción breve
Aplicación web de Help Desk desarrollada con *Flask, **MariaDB, **Bootstrap* y *jQuery*.  
Permite gestionar tickets de soporte, comentarios y usuarios con roles diferenciados (*Admin, **Agent, **User*).  
Incluye autenticación, autorización básica y vistas responsivas para mejorar la experiencia de usuario.

---

## 🛠️ Tecnologías usadas
- *Flask (Python)* – Framework backend y rutas.
- *MariaDB* – Base de datos relacional.
- *Bootstrap 5* – Interfaz responsiva.
- *jQuery* – Interacciones dinámicas y mejoras de UX.
- *Werkzeug* – Hashing seguro de contraseñas.
- *PyMySQL* – Conexión entre Flask y MariaDB.

---

## ⚙️ Variables de entorno requeridas
En el archivo .env deben configurarse las siguientes variables:

SECRET_KEY=pon_aqui_una_clave_larga_y_segura 
DB_HOST=localhost 
DB_USER=helpdesk_user 
DB_PASSWORD=helpdesk_password 
DB_NAME=helpdesk_db
