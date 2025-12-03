# Sistema de Gestión de Archivos y Análisis de Documentos con IA

> **Nota**: Este proyecto fue desarrollado como parte de la resolución de una prueba técnica. Implementa un sistema modular de gestión de archivos CSV y análisis de documentos con Inteligencia Artificial, cumpliendo con todos los requisitos especificados en la prueba.

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Módulos Principales](#módulos-principales)
6. [API Endpoints](#api-endpoints)
7. [Base de Datos](#base-de-datos)
8. [Autenticación y Autorización](#autenticación-y-autorización)
9. [Servicios Externos](#servicios-externos)
10. [Frontend](#frontend)
11. [Configuración](#configuración)
12. [Testing](#testing)
13. [Instalación y Ejecución](#instalación-y-ejecución)
14. [Despliegue](#despliegue)

---

## 📖 Descripción General

Este sistema fue desarrollado como **solución a una prueba técnica** que requería la implementación de un sistema completo de gestión de archivos CSV y análisis de documentos con Inteligencia Artificial.

### Objetivos de la Prueba Técnica

La prueba técnica solicitaba la implementación de:

1. **Módulo de Autenticación**: Sistema de login con JWT y control de roles
2. **Módulo de Archivos CSV**: Carga, validación y almacenamiento en S3
3. **Módulo de Análisis de Documentos con IA**: 
   - Clasificación automática (Factura/Información)
   - Extracción de datos estructurados
   - Integración con AWS Textract
4. **Módulo Histórico**: Log de eventos con filtros y exportación a Excel
5. **Frontend React**: Interfaz moderna con Tailwind CSS
6. **Pruebas Unitarias**: Al menos 10 casos de prueba por método
7. **Refactorización con IA**: Optimización del código usando herramientas de IA

### Funcionalidades Implementadas

El sistema permite:

- **Autenticación y autorización** basada en JWT con control de roles
- **Carga y validación de archivos CSV** con almacenamiento en AWS S3
- **Análisis de documentos** (PDF, JPG, PNG) usando AWS Textract
- **Clasificación automática** de documentos (Facturas vs Información general)
- **Extracción de datos** estructurados de documentos
- **Historial de eventos** completo con exportación a Excel
- **Interfaz web moderna** con React y Tailwind CSS

---

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura modular en capas:

```
┌─────────────────────────────────────────┐
│         Frontend (React + Vite)         │
│     - DocumentUpload                     │
│     - DocumentList                       │
│     - EventHistory                       │
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│      Backend API (FastAPI)               │
│  ┌───────────────────────────────────┐  │
│  │  Middleware                        │  │
│  │  - Auth (JWT)                      │  │
│  │  - Error Handler                   │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Módulos                          │  │
│  │  - Auth                           │  │
│  │  - CSV                            │  │
│  │  - Documents                      │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Servicios Compartidos             │  │
│  │  - S3Service                       │  │
│  │  - TextractService                 │  │
│  │  - CSVValidator                    │  │
│  └───────────────────────────────────┘  │
└─────────┬───────────────┬───────────────┘
          │               │
┌─────────▼──────┐  ┌─────▼──────────────┐
│  SQL Server    │  │  AWS Services      │
│  (Base Datos)  │  │  - S3              │
│                │  │  - Textract        │
└────────────────┘  └───────────────────┘
```

### Principios de Diseño

- **Separación de responsabilidades**: Cada módulo tiene una responsabilidad específica
- **Inversión de dependencias**: Los routers dependen de servicios, no de implementaciones concretas
- **Repository Pattern**: Abstracción de acceso a datos
- **Service Layer**: Lógica de negocio centralizada
- **Middleware**: Manejo centralizado de autenticación y errores

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.11+**: Lenguaje principal
- **FastAPI**: Framework web asíncrono
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación de datos y configuración
- **JWT (python-jose)**: Autenticación con tokens
- **Boto3**: SDK de AWS para S3 y Textract
- **Pytest**: Framework de testing
- **Uvicorn**: Servidor ASGI

### Frontend
- **React 18**: Biblioteca de UI
- **Vite**: Build tool y dev server
- **Tailwind CSS**: Framework de estilos
- **Axios/Fetch**: Cliente HTTP

### Base de Datos
- **SQL Server**: Base de datos relacional
- **ODBC Driver 18**: Conector para SQL Server

### Servicios Cloud
- **AWS S3**: Almacenamiento de archivos
- **AWS Textract**: Análisis de documentos con IA

---

## 📁 Estructura del Proyecto

```
python-prueba-tecnica/
├── python-api/                    # Backend API
│   ├── app/
│   │   ├── main.py               # Punto de entrada FastAPI
│   │   ├── config.py             # Configuración de la aplicación
│   │   ├── database.py           # Configuración de BD
│   │   ├── exceptions/           # Excepciones personalizadas
│   │   ├── middleware/           # Middlewares (auth, error handler)
│   │   ├── modules/              # Módulos de la aplicación
│   │   │   ├── auth/             # Módulo de autenticación
│   │   │   ├── csv/              # Módulo de archivos CSV
│   │   │   └── documents/        # Módulo de documentos
│   │   ├── routers/              # Routers adicionales
│   │   ├── schemas/              # Schemas compartidos
│   │   └── shared/               # Servicios compartidos
│   │       ├── constants.py     # Constantes de la aplicación
│   │       ├── s3_service.py     # Servicio de AWS S3
│   │       ├── textract_service.py  # Servicio de AWS Textract
│   │       └── validators.py     # Validadores de CSV
│   ├── tests/                    # Tests unitarios e integración
│   ├── scripts/                  # Scripts de utilidad
│   └── requirements.txt          # Dependencias Python
│
└── frontend/                     # Frontend React
    ├── src/
    │   ├── components/           # Componentes React
    │   │   ├── Login.jsx
    │   │   ├── DocumentUpload.jsx
    │   │   ├── DocumentList.jsx
    │   │   └── EventHistory.jsx
    │   ├── utils/                # Utilidades
    │   │   └── api.js            # Cliente API
    │   └── App.jsx               # Componente principal
    └── package.json              # Dependencias Node.js
```

---

## 🔧 Módulos Principales

### 1. Módulo de Autenticación (`app/modules/auth/`)

**Responsabilidad**: Gestionar autenticación y autorización de usuarios.

#### Componentes:

- **`models.py`**: Modelos de base de datos (`User`, `Role`)
- **`repository.py`**: Acceso a datos de usuarios y roles
- **`service.py`**: Lógica de autenticación (creación de tokens JWT, verificación)
- **`router.py`**: Endpoints de autenticación
- **`schemas.py`**: Esquemas Pydantic para requests/responses

#### Funcionalidades:

- Login con username/password
- Generación de tokens JWT
- Refresh de tokens
- Registro de eventos de login

### 2. Módulo de Archivos CSV (`app/modules/csv/`)

**Responsabilidad**: Procesar y validar archivos CSV.

#### Componentes:

- **`models.py`**: Modelos `FileUpload` y `CSVRecord`
- **`repository.py`**: Operaciones CRUD de archivos y registros CSV
- **`service.py`**: Lógica de procesamiento de CSV
- **`router.py`**: Endpoints de carga de archivos
- **`schemas.py`**: Esquemas de respuesta

#### Funcionalidades:

- Carga de archivos CSV a S3
- Validación de datos CSV (duplicados, tipos, valores vacíos)
- Almacenamiento de registros en base de datos
- Categorización y descripción de archivos

### 3. Módulo de Documentos (`app/modules/documents/`)

**Responsabilidad**: Análisis de documentos con IA.

#### Componentes:

- **`models.py`**: Modelos `Document` y `EventLog`
- **`repository.py`**: Operaciones CRUD de documentos y eventos
- **`service.py`**: Lógica de análisis de documentos
- **`router.py`**: Endpoints de documentos y eventos
- **`schemas.py`**: Esquemas de respuesta

#### Funcionalidades:

- Carga de documentos (PDF, JPG, PNG)
- Análisis con AWS Textract
- Clasificación automática (Factura/Información)
- Extracción de datos estructurados
- Historial de eventos con filtros
- Exportación a Excel

---

## 🌐 API Endpoints

### Autenticación (`/auth`)

#### `POST /auth/login`
Inicia sesión y obtiene un token JWT.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### `POST /auth/refresh`
Renueva un token JWT.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Archivos CSV (`/files`)

#### `POST /files/upload`
Sube y valida un archivo CSV.

**Requisitos**: Rol `admin` o `uploader`

**Request**: `multipart/form-data`
- `file`: Archivo CSV
- `categoria` (opcional): Categoría del archivo
- `descripcion` (opcional): Descripción del archivo

**Response:**
```json
{
  "file_id": 1,
  "filename": "datos.csv",
  "s3_url": "https://bucket.s3.amazonaws.com/...",
  "status": "completed",
  "validations": [...],
  "records_count": 100,
  "categoria": "ventas",
  "descripcion": "Datos de ventas Q1"
}
```

**Validaciones aplicadas:**
- Valores vacíos
- Tipos de datos incorrectos
- Duplicados
- Formato CSV inválido

---

### Documentos (`/documents`)

#### `POST /documents/upload`
Sube y analiza un documento con IA.

**Requisitos**: Usuario autenticado

**Request**: `multipart/form-data`
- `file`: Archivo PDF, JPG o PNG (máx. 10MB)

**Response:**
```json
{
  "id": 1,
  "filename": "factura.pdf",
  "s3_url": "https://bucket.s3.amazonaws.com/...",
  "classification": "Factura",
  "status": "completed",
  "extracted_data": {
    "cliente": {...},
    "proveedor": {...},
    "total": "1000.00",
    "productos": [...]
  }
}
```

#### `GET /documents/`
Obtiene lista de documentos del usuario.

**Query Parameters:**
- `classification` (opcional): Filtrar por clasificación
- `limit` (default: 100): Límite de resultados
- `offset` (default: 0): Offset de paginación

#### `GET /documents/{document_id}`
Obtiene un documento específico.

#### `GET /documents/events/history`
Obtiene historial de eventos con filtros.

**Query Parameters:**
- `event_type` (opcional): Tipo de evento
- `description` (opcional): Buscar en descripción
- `start_date` (opcional): Fecha inicio (YYYY-MM-DD)
- `end_date` (opcional): Fecha fin (YYYY-MM-DD)
- `limit` (default: 100)
- `offset` (default: 0)

#### `GET /documents/events/export`
Exporta eventos a Excel con los mismos filtros.

---

## 🗄️ Base de Datos

### Esquema de Tablas

#### `users`
Almacena información de usuarios.

```sql
- id (PK, INT)
- username (VARCHAR, UNIQUE)
- password_hash (VARCHAR)
- role_id (FK -> roles.id)
- created_at (DATETIME)
- updated_at (DATETIME)
```

#### `roles`
Define roles del sistema.

```sql
- id (PK, INT)
- name (VARCHAR, UNIQUE)  -- 'admin', 'uploader', 'user'
- description (VARCHAR)
```

#### `file_uploads`
Registra archivos CSV subidos.

```sql
- id (PK, INT)
- original_filename (VARCHAR)
- s3_key (VARCHAR, UNIQUE)
- s3_url (VARCHAR)
- user_id (FK -> users.id)
- status (VARCHAR)  -- 'processing', 'completed', 'error'
- validations (TEXT/JSON)
- records_count (INT)
- categoria (VARCHAR)
- descripcion (VARCHAR)
- created_at (DATETIME)
```

#### `csv_records`
Almacena registros individuales de CSV.

```sql
- id (PK, INT)
- file_upload_id (FK -> file_uploads.id)
- row_number (INT)
- record_data (TEXT/JSON)
- is_valid (VARCHAR)  -- 'true', 'false'
- validation_errors (TEXT/JSON)
- created_at (DATETIME)
```

#### `documents`
Registra documentos analizados.

```sql
- id (PK, INT)
- original_filename (VARCHAR)
- file_type (VARCHAR)  -- 'PDF', 'JPG', 'PNG'
- s3_key (VARCHAR, UNIQUE)
- s3_url (VARCHAR)
- user_id (FK -> users.id)
- classification (VARCHAR)  -- 'Factura', 'Información'
- status (VARCHAR)  -- 'processing', 'completed', 'error'
- extracted_data (TEXT/JSON)
- created_at (DATETIME)
- updated_at (DATETIME)
```

#### `event_logs`
Registra eventos del sistema.

```sql
- id (PK, INT)
- document_id (FK -> documents.id, NULLABLE)
- event_type (VARCHAR)  -- 'user_login', 'document_upload', 'ai_analysis'
- description (TEXT)
- event_metadata (TEXT/JSON)
- user_id (FK -> users.id, NULLABLE)
- created_at (DATETIME)
```

### Relaciones

- `users` → `roles` (Many-to-One)
- `users` → `file_uploads` (One-to-Many)
- `users` → `documents` (One-to-Many)
- `users` → `event_logs` (One-to-Many)
- `file_uploads` → `csv_records` (One-to-Many)
- `documents` → `event_logs` (One-to-Many)

---

## 🔐 Autenticación y Autorización

### Flujo de Autenticación

1. Usuario envía credenciales a `/auth/login`
2. Sistema valida credenciales contra la base de datos
3. Si son válidas, se genera un JWT con:
   - `id_usuario`: ID del usuario
   - `rol`: Rol del usuario (normalizado a lowercase)
   - `jti`: JWT ID único
   - `iat`: Fecha de emisión
   - `exp`: Fecha de expiración
4. Se registra evento de login en `event_logs`
5. Se retorna el token al cliente

### Autorización por Roles

El sistema tiene tres roles:

- **`admin`**: Acceso completo
- **`uploader`**: Puede subir archivos CSV y documentos
- **`user`**: Acceso limitado (solo lectura de sus propios documentos)

### Middleware de Autenticación

El middleware `get_current_user` valida el token JWT en cada request:

```python
@router.get("/protected")
async def protected_endpoint(
    current_user: TokenData = Depends(get_current_user)
):
    # current_user contiene id_usuario y rol
    ...
```

### Control de Acceso por Rol

```python
@router.post("/upload")
async def upload_file(
    current_user: TokenData = Depends(require_role(["admin", "uploader"]))
):
    # Solo admin y uploader pueden acceder
    ...
```

---

## ☁️ Servicios Externos

### AWS S3

**Servicio**: `app/shared/s3_service.py`

**Funcionalidades:**
- `upload_file()`: Sube archivos a S3 con metadata
- `delete_file()`: Elimina archivos de S3
- `file_exists()`: Verifica existencia de archivos

**Estructura de almacenamiento:**
```
bucket/
├── uploads/
│   ├── YYYY/MM/DD/
│   │   └── filename.csv
│   └── documentos/
│       └── YYYY/MM/DD/
│           └── documento.pdf
```

**Metadata almacenada:**
- `categoria`: Categoría del archivo
- `descripcion`: Descripción del archivo
- `user_id`: ID del usuario que subió el archivo

### AWS Textract

**Servicio**: `app/shared/textract_service.py`

**Funcionalidades:**
- `detect_document_text()`: Extrae texto de documentos
- `analyze_document()`: Análisis completo con FORMS y TABLES
- `classify_document()`: Clasifica como Factura o Información
- `extract_invoice_data()`: Extrae datos estructurados de facturas
- `extract_information_data()`: Extrae información general con análisis de sentimiento

**Clasificación de Documentos:**

El sistema clasifica documentos basándose en palabras clave:

**Factura** (si encuentra ≥3 keywords):
- factura, invoice, total, subtotal, iva, impuesto
- cliente, proveedor, supplier, customer
- producto, cantidad, precio
- número de factura, fecha de emisión

**Información** (si encuentra <3 keywords):
- Cualquier otro documento

**Extracción de Datos:**

Para **Facturas**:
- Cliente (nombre, dirección)
- Proveedor (nombre, dirección)
- Número de factura
- Fecha
- Productos (cantidad, nombre, precio, total)
- Total de la factura

Para **Información**:
- Descripción
- Resumen (primeros 200 caracteres)
- Análisis de sentimiento (positivo/negativo/neutral)

---

## 🎨 Frontend

### Arquitectura

El frontend está construido con React y usa un patrón de componentes funcionales con hooks.

### Componentes Principales

#### `App.jsx`
Componente raíz que maneja:
- Estado de autenticación
- Navegación por tabs
- Redirección a login en caso de 401

#### `Login.jsx`
Formulario de inicio de sesión con:
- Validación de campos
- Manejo de errores
- Loading states

#### `DocumentUpload.jsx`
Componente para subir documentos:
- Drag & drop (preparado)
- Validación de tipo de archivo
- Feedback visual del progreso

#### `DocumentList.jsx`
Lista de documentos del usuario:
- Filtrado por clasificación
- Visualización de datos extraídos
- Enlaces a archivos en S3

#### `EventHistory.jsx`
Historial completo de eventos:
- Filtros por tipo, descripción, fecha
- Tabla responsive
- Exportación a Excel

### Utilidades

#### `api.js`
Cliente HTTP centralizado que:
- Agrega token JWT automáticamente
- Maneja errores 401 (redirige a login)
- Formatea requests/responses

### Estilos

- **Tailwind CSS**: Framework utility-first
- **Tema**: Azul profesional estilo Microsoft
- **Responsive**: Diseño adaptable a móviles

---

## ⚙️ Configuración

### Variables de Entorno

Crear archivo `.env` en `python-api/`:

```env
# JWT
SECRET_KEY=tu-clave-secreta-super-segura
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# AWS
AWS_ACCESS_KEY_ID=tu_access_key_id
AWS_SECRET_ACCESS_KEY=tu_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=nombre-de-tu-bucket

# SQL Server
SQL_SERVER_HOST=localhost
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=prueba_tecnica
SQL_SERVER_USER=sa
SQL_SERVER_PASSWORD=tu_password
SQL_SERVER_DRIVER=ODBC Driver 18 for SQL Server
```

### Frontend

Crear archivo `.env` en `frontend/`:

```env
VITE_API_URL=http://127.0.0.1:8001
```

---

## 🧪 Testing

### Estructura de Tests

Los tests están organizados por módulo:

```
tests/
├── test_auth.py              # Tests de autenticación
├── test_documents.py         # Tests de documentos
├── test_files.py            # Tests de archivos CSV
├── test_services.py         # Tests de servicios
├── test_repositories.py     # Tests de repositorios
├── test_middleware.py       # Tests de middleware
├── test_validators.py       # Tests de validadores
└── test_textract_service.py # Tests de Textract
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_auth.py

# Con cobertura
pytest --cov=app tests/

# Verbose
pytest -v
```

### Cobertura Actual

- **158 tests** pasando
- Cobertura de todos los módulos principales
- Tests unitarios e integración
- Mocks para servicios externos (S3, Textract)

---

## 🚀 Instalación y Ejecución

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- SQL Server con ODBC Driver 18
- Cuenta de AWS con S3 y Textract configurados

### Backend

```bash
# 1. Crear entorno virtual
cd python-api
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# 4. Inicializar base de datos
python scripts/init_users.py

# 5. Ejecutar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend

```bash
# 1. Instalar dependencias
cd frontend
npm install

# 2. Configurar .env
echo "VITE_API_URL=http://127.0.0.1:8001" > .env

# 3. Ejecutar servidor de desarrollo
npm run dev
```

### Acceso

- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Frontend**: http://localhost:5173

### Usuarios por Defecto

```
Admin:    usuario=admin,    password=admin123
Uploader: usuario=uploader, password=uploader123
User:     usuario=user,     password=user123
```

---

## 📦 Despliegue

### Consideraciones de Producción

1. **Seguridad**:
   - Cambiar `SECRET_KEY` por una clave segura
   - Configurar CORS con orígenes específicos
   - Usar HTTPS
   - Validar y sanitizar todas las entradas

2. **Base de Datos**:
   - Usar connection pooling
   - Configurar backups automáticos
   - Monitorear performance

3. **AWS**:
   - Usar IAM roles en lugar de credenciales hardcodeadas
   - Configurar políticas de acceso mínimas
   - Habilitar versionado en S3
   - Configurar lifecycle policies

4. **Logging**:
   - Configurar logging estructurado
   - Integrar con servicios de monitoreo (CloudWatch, etc.)
   - Logs de errores con contexto completo

5. **Performance**:
   - Cachear resultados de Textract cuando sea posible
   - Implementar rate limiting
   - Optimizar queries de base de datos
   - Usar CDN para archivos estáticos

### Docker (Opcional)

```dockerfile
# Dockerfile para backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 📝 Notas Adicionales

### Manejo de Errores

El sistema tiene un manejo centralizado de errores:

- **Middleware de errores**: Captura todas las excepciones
- **Rollback automático**: Transacciones se revierten en caso de error
- **Logging**: Todos los errores se registran con contexto
- **Formato consistente**: Todas las respuestas de error tienen el mismo formato

### Constantes y Configuración

Las constantes están centralizadas en `app/shared/constants.py`:

- Enums para estados y clasificaciones
- Palabras clave para clasificación
- Límites y umbrales configurables

### Refactorizaciones Realizadas

1. **Centralización de constantes**: Eliminación de strings mágicos
2. **Mejora de transacciones**: Rollback automático
3. **Validaciones**: Tamaño de archivo, archivos vacíos
4. **Manejo de errores**: Mejor logging y recuperación

---

## 🎯 Requisitos de la Prueba Técnica

Este proyecto cumple con todos los requisitos especificados en la prueba técnica:

### ✅ Parte 1: Módulos Backend
- [x] Autenticación con JWT y control de roles
- [x] Carga y validación de archivos CSV
- [x] Almacenamiento en AWS S3
- [x] Base de datos SQL Server con SQLAlchemy
- [x] Manejo de errores centralizado

### ✅ Parte 2: Módulos Web (Análisis de Documentos con IA)
- [x] Pantalla para cargar documentos (PDF, JPG, PNG)
- [x] Clasificación automática (Factura/Información)
- [x] Extracción automática de datos:
  - Facturas: Cliente, Proveedor, Número, Fecha, Productos, Total
  - Información: Descripción, Resumen, Análisis de sentimiento
- [x] Integración con AWS Textract
- [x] Módulo histórico con filtros y exportación a Excel

### ✅ Parte 3: Uso de IA y Refactorización
- [x] Refactorización dinámica con herramientas de IA (Cursor)
- [x] Documentación generada con IA para cada función
- [x] Pruebas unitarias: 158 tests (mínimo 10 por método en módulos principales)
- [x] Control de versiones en GitHub con commits descriptivos

### Tecnologías Obligatorias
- [x] Python (FastAPI)
- [x] AWS S3 para almacenamiento
- [x] SQL Server (SQLAlchemy para ORM)
- [x] JWT para autenticación y control de roles
- [x] GitHub para control de versiones
- [x] Herramientas de IA para extracción, refactorización y pruebas

### Criterios de Evaluación Cumplidos
- ✅ **Estructura del Código**: Modularidad, claridad y buenas prácticas
- ✅ **Eficiencia de APIs**: Manejo de tokens, roles y restricciones de acceso
- ✅ **Integración con IA**: Uso efectivo de AWS Textract y herramientas de desarrollo
- ✅ **Calidad del Log y Exportación**: Funcionalidad completa del histórico y Excel
- ✅ **Pruebas Unitarias**: 158 tests con cobertura completa
- ✅ **Control de Cambios**: Commits claros y descriptivos en GitHub

---

## 🤝 Desarrollo

Este proyecto fue desarrollado como **solución a una prueba técnica**, siguiendo buenas prácticas de desarrollo:

- Código modular y mantenible
- Tests comprehensivos (158 tests)
- Documentación completa
- Manejo robusto de errores
- Integración con servicios cloud (AWS S3, Textract)
- Refactorización con herramientas de IA (Cursor)
- Frontend moderno con React y Tailwind CSS

### Commits de Refactorización

El proyecto incluye commits de refactorización realizados con herramientas de IA:

- `Refactorización con [Cursor]: Centralización de constantes y eliminación de código duplicado`
- `Refactorización con [Cursor]: Mejoras en manejo de errores y transacciones`

---

## 📄 Licencia

Este proyecto fue desarrollado como parte de una prueba técnica y no tiene licencia específica.

---

## 📊 Estadísticas del Proyecto

- **Líneas de código**: ~15,000+
- **Tests**: 158 tests unitarios e integración
- **Módulos**: 3 módulos principales (Auth, CSV, Documents)
- **Endpoints API**: 10+ endpoints REST
- **Componentes Frontend**: 4 componentes principales
- **Cobertura de tests**: Todos los módulos principales cubiertos

---

**Versión**: 1.0.0  
**Desarrollado como**: Prueba Técnica  
**Última actualización**: Diciembre 2024

