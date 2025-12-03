"""
Script de inicialización para crear usuarios de ejemplo.
Ejecutar este script para crear usuarios iniciales en la base de datos.
"""
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.repositories.user_repository import UserRepository


def create_initial_users():
    """
    Crea usuarios iniciales en la base de datos.
    """
    # Inicializar la base de datos
    init_db()
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        user_repository = UserRepository(db)
        
        # Crear usuario administrador
        admin_user = user_repository.create_user(
            username="admin",
            password="admin123",
            role_name="admin"
        )
        print(f"✓ Usuario administrador creado: {admin_user.username} (ID: {admin_user.id})")
        
        # Crear usuario con rol uploader
        uploader_user = user_repository.create_user(
            username="uploader",
            password="uploader123",
            role_name="uploader"
        )
        print(f"✓ Usuario uploader creado: {uploader_user.username} (ID: {uploader_user.id})")
        
        # Crear usuario normal
        normal_user = user_repository.create_user(
            username="user",
            password="user123",
            role_name="user"
        )
        print(f"✓ Usuario normal creado: {normal_user.username} (ID: {normal_user.id})")
        
        print("\n✓ Usuarios iniciales creados exitosamente!")
        print("\nCredenciales:")
        print("  Admin:    usuario=admin,    password=admin123")
        print("  Uploader: usuario=uploader, password=uploader123")
        print("  User:     usuario=user,     password=user123")
        
    except Exception as e:
        print(f"✗ Error al crear usuarios: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_users()

