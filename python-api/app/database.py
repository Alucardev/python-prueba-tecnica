"""
Configuración de la base de datos.
Maneja la conexión y sesiones de SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.shared.models import Base

# Crear el motor de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    echo=False  # Cambiar a True para ver las queries SQL en consola
)

# Crear la clase SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Inicializa las tablas en la base de datos.
    Crea todas las tablas definidas en los modelos.
    """
    # Importar todos los modelos para que SQLAlchemy los registre
    from app.modules.auth import models as auth_models  # noqa: F401
    from app.modules.csv import models as csv_models  # noqa: F401
    
    # Crear todas las tablas usando la Base compartida
    Base.metadata.create_all(bind=engine)
    
    # Crear roles iniciales si no existen
    _create_initial_roles()


def _create_initial_roles():
    """
    Crea los roles iniciales en la base de datos si no existen.
    """
    from app.modules.auth.repository import RoleRepository
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        role_repo = RoleRepository(db)
        
        # Roles iniciales
        initial_roles = [
            {"name": "admin", "description": "Administrador del sistema"},
            {"name": "uploader", "description": "Usuario con permisos para subir archivos"},
            {"name": "user", "description": "Usuario estándar"}
        ]
        
        for role_data in initial_roles:
            existing_role = role_repo.get_by_name(role_data["name"])
            if not existing_role:
                role_repo.create_role(
                    name=role_data["name"],
                    description=role_data["description"]
                )
    finally:
        db.close()


def get_db() -> Session:
    """
    Generador de sesiones de base de datos.
    Proporciona una sesión de base de datos y la cierra automáticamente.
    
    Yields:
        Sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

