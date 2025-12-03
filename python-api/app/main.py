"""
Aplicación principal FastAPI.
Punto de entrada de la aplicación y configuración de la API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, files
from app.middleware.error_handler import error_handler_middleware

# Crear la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Archivos CSV",
    description="API REST para autenticación, carga y validación de archivos CSV con integración AWS S3 y SQL Server",
    version="1.0.0"
)

# Registrar middleware de manejo de errores (debe ir antes de otros middlewares)
app.middleware("http")(error_handler_middleware)

# Configurar CORS (permitir solicitudes desde cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar la base de datos al iniciar la aplicación
@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    Inicializa las tablas de la base de datos.
    """
    init_db()


# Incluir los routers
app.include_router(auth.router)
app.include_router(files.router)


@app.get("/", tags=["Raíz"])
async def root():
    """
    Endpoint raíz de la API.
    
    Returns:
        Mensaje de bienvenida
    """
    return {
        "message": "API de Gestión de Archivos CSV",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth/login, /auth/refresh",
            "files": "/files/upload"
        }
    }


@app.get("/health", tags=["Salud"])
async def health_check():
    """
    Endpoint de verificación de salud de la API.
    
    Returns:
        Estado de la aplicación
    """
    return {"status": "healthy"}

