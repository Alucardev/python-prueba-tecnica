"""
Base compartida para todos los modelos.
Todos los modelos deben usar esta Base para que SQLAlchemy pueda manejar las relaciones.
"""
from sqlalchemy.ext.declarative import declarative_base

# Base compartida para todos los modelos
Base = declarative_base()

