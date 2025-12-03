"""
Configuración global de pytest.
Define fixtures compartidas para todos los tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_db
from app.shared.models import Base
from app.modules.auth.repository import UserRepository, RoleRepository
import os

# Configurar base de datos de prueba en memoria (SQLite para tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Crea una sesión de base de datos de prueba para cada test.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

    # Crear roles iniciales para los tests (admin, uploader, user)
    session = TestingSessionLocal()
    try:
        role_repo = RoleRepository(session)
        initial_roles = [
            {"name": "admin", "description": "Administrador del sistema"},
            {"name": "uploader", "description": "Usuario con permisos para subir archivos"},
            {"name": "user", "description": "Usuario estándar"},
        ]
        for role_data in initial_roles:
            existing_role = role_repo.get_by_name(role_data["name"])
            if not existing_role:
                role_repo.create_role(
                    name=role_data["name"],
                    description=role_data["description"],
                )
        session.commit()
    finally:
        session.close()

    # Crear sesión
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Limpiar tablas después de cada test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Crea un cliente de prueba para la API.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """
    Crea un usuario de prueba en la base de datos.
    """
    user_repository = UserRepository(db_session)
    user = user_repository.create_user(
        username="testuser",
        password="testpassword123",
        role_name="user"
    )
    return user


@pytest.fixture
def test_admin_user(db_session):
    """
    Crea un usuario administrador de prueba.
    """
    user_repository = UserRepository(db_session)
    user = user_repository.create_user(
        username="admin",
        password="admin123",
        role_name="admin"
    )
    return user


@pytest.fixture
def test_uploader_user(db_session):
    """
    Crea un usuario con rol uploader de prueba.
    """
    user_repository = UserRepository(db_session)
    user = user_repository.create_user(
        username="uploader",
        password="uploader123",
        role_name="uploader"
    )
    return user


@pytest.fixture
def auth_token(client, test_user):
    """
    Obtiene un token JWT para un usuario de prueba.
    """
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, test_admin_user):
    """
    Obtiene un token JWT para un usuario administrador.
    """
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def uploader_token(client, test_uploader_user):
    """
    Obtiene un token JWT para un usuario uploader.
    """
    response = client.post(
        "/auth/login",
        json={"username": "uploader", "password": "uploader123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def sample_csv_content():
    """
    Retorna contenido de un CSV de ejemplo para tests.
    """
    csv_text = """id,nombre,email,edad,ciudad
1,Juan Pérez,juan@example.com,30,Madrid
2,María García,maria@example.com,25,Barcelona
3,Carlos López,carlos@example.com,35,Valencia"""
    return csv_text.encode("utf-8")


@pytest.fixture
def sample_csv_file(sample_csv_content):
    """
    Crea un archivo CSV de prueba en memoria.
    """
    from io import BytesIO
    return ("test.csv", BytesIO(sample_csv_content), "text/csv")

