"""
Aplicación principal FastAPI.
Punto de entrada de la aplicación y configuración de la API.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.database import init_db
from app.middleware.error_handler import error_handler_middleware
from app.modules.auth.router import router as auth_router
from app.modules.csv.router import router as csv_router
from app.modules.documents.router import router as documents_router

# Crear la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Archivos CSV",
    description="API REST para autenticación, carga y validación de archivos CSV con integración AWS S3 y SQL Server",
    version="1.0.0"
)

# Registrar middleware de manejo de errores (debe ir antes de otros middlewares)
app.middleware("http")(error_handler_middleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador global para errores de validación de Pydantic.
    Devuelve el mismo formato esperado por los tests.
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", ""),
                "type": error.get("type", ""),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Error de validación en los datos enviados",
            "type": "ValidationError",
            "details": errors,
        },
    )

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


# Incluir los routers de los módulos
app.include_router(auth_router)
app.include_router(csv_router)
app.include_router(documents_router)


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
            "files": "/files/upload",
            "documents": "/documents/upload, /documents/, /documents/events/history"
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

