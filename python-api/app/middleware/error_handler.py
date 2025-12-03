"""
Middleware de manejo de errores centralizado.
Captura y formatea todas las excepciones de la aplicación.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions.custom_exceptions import BaseAppException
import logging
import traceback

# Configurar logger
logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Middleware centralizado para manejo de errores.
    Captura todas las excepciones y las formatea de manera consistente.
    
    Args:
        request: Request de FastAPI
        call_next: Función para continuar con el siguiente middleware
        
    Returns:
        Response formateada con el error
    """
    try:
        # Continuar con el request
        response = await call_next(request)
        return response
        
    except BaseAppException as e:
        # Excepciones personalizadas de la aplicación
        logger.warning(f"Excepción de aplicación: {e.message}", exc_info=True)
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": True,
                "message": e.message,
                "type": e.__class__.__name__
            }
        )
        
    except RequestValidationError as e:
        # Errores de validación de Pydantic
        logger.warning(f"Error de validación: {str(e)}")
        errors = []
        for error in e.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", ""),
                "type": error.get("type", "")
            })
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "message": "Error de validación en los datos enviados",
                "type": "ValidationError",
                "details": errors
            }
        )
        
    except StarletteHTTPException as e:
        # Excepciones HTTP de Starlette/FastAPI
        logger.warning(f"Excepción HTTP: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": True,
                "message": e.detail,
                "type": "HTTPException"
            }
        )
        
    except SQLAlchemyError as e:
        # Errores de SQLAlchemy
        logger.error(f"Error de base de datos: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "Error en la base de datos",
                "type": "DatabaseError"
            }
        )
        
    except Exception as e:
        # Cualquier otra excepción no manejada
        logger.error(f"Error no manejado: {str(e)}", exc_info=True)
        # En desarrollo, incluir el traceback completo
        import os
        is_development = os.getenv("ENVIRONMENT", "development") == "development"
        
        error_response = {
            "error": True,
            "message": "Error interno del servidor",
            "type": "InternalServerError"
        }
        
        if is_development:
            error_response["detail"] = str(e)
            error_response["traceback"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )

