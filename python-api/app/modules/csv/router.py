"""
Router del módulo CSV.

Se apoya en el router existente de archivos para respetar la estructura modular.
"""
from app.routers.files import router  # noqa: F401

__all__ = ["router"]


