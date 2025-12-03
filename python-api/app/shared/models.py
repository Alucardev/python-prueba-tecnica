"""
Modelos y base ORM compartidos entre módulos.
"""
from sqlalchemy.ext.declarative import declarative_base

# Base compartida para todos los modelos
Base = declarative_base()

__all__ = ["Base"]


