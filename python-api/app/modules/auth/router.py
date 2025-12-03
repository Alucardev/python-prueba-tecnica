"""
Router del módulo de autenticación.

Se limita a importar y reexponer el router existente para migrar hacia
una estructura modular sin romper el código actual.
"""
from app.routers.auth import router  # noqa: F401

__all__ = ["router"]


