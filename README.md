# 🏠 Sistema de Gestión de Propiedades - Backend

Un sistema completo de gestión de propiedades vacacionales desarrollado con Flask, que incluye autenticación, gestión de unidades, reservas, reportes y una API pública para terceros.

## 🚀 Características Principales

- **🔐 Autenticación JWT** con roles de administrador y super administrador
- **🏘️ Gestión de Unidades** - Crear, editar, eliminar y buscar propiedades
- **📅 Sistema de Reservas** con validación de disponibilidad
- **📊 Reportes Automatizados** con gráficos de ingresos y ocupación
- **💰 Multiplicadores de Precios** por temporada y ocupación
- **📧 Notificaciones por Email** para check-in y recuperación de contraseñas
- **🌐 API Pública** para integración con terceros
- **📱 CORS habilitado** para frontend

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask 3.1.0
- **Base de Datos**: MySQL
- **Autenticación**: JWT (JSON Web Tokens)
- **Email**: Flask-Mail con Gmail OAuth2
- **Deployment**: Render
- **CORS**: Flask-CORS

## 🌐 **API en Producción**

**URL Base**: [https://proyectoppvi.onrender.com/](https://proyectoppvi.onrender.com/)

**Documentación de Endpoints**: [https://proyectoppvi.onrender.com/](https://proyectoppvi.onrender.com/)

## 📋 Requisitos Previos

- Python 3.8+
- MySQL Server
- Cuenta de Gmail para envío de emails
- Cuenta de Render (para deployment)

## ⚙️ Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd ProyectoPPVI
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración de Base de Datos
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_PORT=3306
DB_NAME=nombre_base_datos

# Configuración JWT
JWT_SECRET_KEY=tu_clave_secreta_jwt
SECRET_KEY=tu_clave_secreta_flask

# Configuración de Email
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_DEFAULT_SENDER=tu_email@gmail.com

# URL del Frontend
URL_FRONT=http://localhost:3000
```

### 5. Configurar Base de Datos

Ejecutar los comandos SQL del archivo `resources/comandosSQL.txt` en tu servidor MySQL.

### 6. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🌐 Endpoints de la API

### 🔐 Autenticación

#### POST `/login`

Autenticación de administradores

```json
{
  "username": "admin@email.com",
  "password": "contraseña"
}
```

**Respuesta**: JWT token + información de superUser

#### POST `/crearAdmin`

Crear nuevo administrador (requiere superUser)

```json
{
  "username": "nuevo@email.com",
  "password": "contraseña",
  "superUser": false
}
```

#### GET `/recoveryPass`

Recuperación de contraseña

```
/recoveryPass?username=admin@email.com
```

### 🏘️ Gestión de Unidades

#### POST `/crearUnidad`

Crear nueva unidad

```json
{
  "rooms": 2,
  "beds": 4,
  "description": "Hermosa casa con vista al mar",
  "price": 150.0,
  "amenities": ["WiFi", "Piscina", "Estacionamiento"],
  "urls_fotos": ["url1.jpg", "url2.jpg"],
  "title": "Casa en la Playa",
  "bathrooms": 2,
  "address": "Calle Principal 123"
}
```

#### POST `/editarUnidad`

Editar unidad existente

```json
{
  "id": 1,
  "rooms": 3,
  "beds": 6,
  "price": 200.0
  // ... otros campos
}
```

#### POST `/eliminarUnidad`

Eliminar unidad

```json
{
  "id": 1
}
```

### 🔍 API Pública para Terceros

#### GET `/api/terceros/units/`

Buscar unidades disponibles

```
/api/terceros/units/?check_in_date=2024-02-01&check_out_date=2024-02-05&rooms=2&beds=4
```

#### POST `/api/terceros/units/`

Buscar unidades con filtros avanzados

```json
{
  "check_in_date": "2024-02-01",
  "check_out_date": "2024-02-05",
  "rooms": 2,
  "beds": 4,
  "amenities": ["WiFi", "Piscina"]
}
```

#### POST `/api/terceros/almacenaReserva`

Crear nueva reserva

```json
{
  "unit_id": 1,
  "check_in_date": "2024-02-01",
  "check_out_date": "2024-02-05",
  "price": 150.0,
  "amount_paid": 75.0,
  "guest": {
    "name": "Juan Pérez",
    "mail": "juan@email.com",
    "phone": "+1234567890"
  }
}
```

### 📊 Reportes y Gestión

#### GET `/informes`

Generar y enviar reportes por email (requiere autenticación)

#### GET `/verReservas`

Ver todas las reservas del sistema

#### POST `/motor`

Calcular multiplicadores de precios por temporada

### 🔗 Otros Endpoints

#### GET `/`

Información de todos los endpoints disponibles

#### GET `/verAdmins`

Listar administradores (requiere superUser)

#### DELETE `/deleteAdmin/<id>`

Eliminar administrador (requiere superUser)

#### POST `/editPass`

Cambiar contraseña del administrador logueado

## 🚀 Deployment en Render

### 1. Preparar la Aplicación

El proyecto ya incluye:

- `requirements.txt` con todas las dependencias
- Configuración de Gunicorn en `Procfile`

### 2. Crear Aplicación en Render

1. Ve a [render.com](https://render.com) y crea una cuenta
2. Haz clic en "New +" y selecciona "Web Service"
3. Conecta tu repositorio de GitHub
4. Configura el servicio:
   - **Name**: `proyectoppvi` (o el nombre que prefieras)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Configurar Variables de Entorno

En la sección "Environment Variables" de Render, agrega:

```env
DB_HOST=tu-host-mysql
DB_USER=tu-usuario-mysql
DB_PASSWORD=tu-contraseña-mysql
DB_PORT=3306
DB_NAME=tu-base-datos
JWT_SECRET_KEY=tu-clave-secreta-jwt
SECRET_KEY=tu-clave-secreta-flask
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicacion
MAIL_DEFAULT_SENDER=tu-email@gmail.com
URL_FRONT=https://tu-frontend.com
```

### 4. Desplegar

1. Render detectará automáticamente los cambios en tu repositorio
2. Cada push a la rama principal activará un nuevo deployment
3. La aplicación estará disponible en `https://tu-app-name.onrender.com`

### 5. Configuración de Base de Datos

Para producción, se recomienda usar:

- **PlanetScale** (MySQL compatible)
- **AWS RDS** (MySQL)
- **Google Cloud SQL** (MySQL)

## 🧪 Testing

### Tests con Postman

El proyecto incluye colecciones de tests en:

- `test/api/DB/test_postman.json`
- `test/api/DB/test_tunder.json`

### Ejecutar Tests

1. Importar la colección en Postman
2. Configurar variables de entorno
3. Ejecutar todos los tests

## 📁 Estructura del Proyecto

```
ProyectoPPVI/
├── app.py                 # Aplicación principal Flask
├── controllerDB.py        # Controlador de base de datos
├── clases/               # Clases del sistema
│   ├── admin.py         # Gestión de administradores
│   ├── guest.py         # Gestión de huéspedes
│   ├── reports.py       # Generación de reportes
│   ├── reservation.py   # Gestión de reservas
│   └── unit.py          # Gestión de unidades
├── templates/mails/      # Plantillas de email
├── resources/           # Recursos del sistema
├── test/               # Tests de la API
└── requirements.txt    # Dependencias de Python
```

## 🔧 Configuración de Email

Para el envío de emails, necesitas:

1. Habilitar autenticación de 2 factores en Gmail
2. Generar una contraseña de aplicación
3. Usar esa contraseña en `MAIL_PASSWORD`

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si tienes alguna pregunta o necesitas ayuda:

- Revisa la documentación de endpoints en `/`
- Consulta los tests en Postman
- Abre un issue en el repositorio

---
