"""
Tests para los repositorios de la aplicación.
"""
import pytest
from app.modules.auth.repository import UserRepository
from app.modules.csv.repository import FileRepository


class TestUserRepository:
    """Tests para el repositorio de usuarios."""
    
    def test_create_user(self, db_session):
        """Test de creación de usuario."""
        user_repository = UserRepository(db_session)
        
        user = user_repository.create_user(
            username="newuser",
            password="password123",
            role_name="user"
        )
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.role == "user"  # Ahora es un string del nombre del rol
        assert user.password_hash != "password123"  # Debe estar hasheada
    
    def test_get_by_username(self, db_session, test_user):
        """Test de obtención de usuario por username."""
        user_repository = UserRepository(db_session)
        
        user = user_repository.get_by_username("testuser")
        
        assert user is not None
        assert user.username == "testuser"
        assert user.id == test_user.id
    
    def test_get_by_username_not_found(self, db_session):
        """Test de obtención de usuario inexistente."""
        user_repository = UserRepository(db_session)
        
        user = user_repository.get_by_username("nonexistent")
        
        assert user is None
    
    def test_get_by_id(self, db_session, test_user):
        """Test de obtención de usuario por ID."""
        user_repository = UserRepository(db_session)
        
        user = user_repository.get_by_id(test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == "testuser"
    
    def test_verify_password(self, db_session):
        """Test de verificación de contraseña."""
        user_repository = UserRepository(db_session)
        
        user = user_repository.create_user(
            username="test",
            password="mypassword",
            role_name="user"
        )
        
        # Verificar contraseña correcta
        assert user_repository.verify_password("mypassword", user.password_hash) is True
        
        # Verificar contraseña incorrecta
        assert user_repository.verify_password("wrongpassword", user.password_hash) is False
    
    def test_hash_password(self, db_session):
        """Test de hashing de contraseña."""
        user_repository = UserRepository(db_session)
        
        password = "testpassword"
        hashed = user_repository.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        # Verificar que el hash es diferente cada vez (por el salt)
        hashed2 = user_repository.hash_password(password)
        assert hashed != hashed2  # Diferentes salts, diferentes hashes


class TestFileRepository:
    """Tests para el repositorio de archivos."""
    
    def test_create_file_upload(self, db_session, test_user):
        """Test de creación de registro de archivo."""
        file_repository = FileRepository(db_session)
        
        file_upload = file_repository.create_file_upload(
            original_filename="test.csv",
            s3_key="uploads/test.csv",
            s3_url="https://bucket.s3.amazonaws.com/uploads/test.csv",
            user_id=test_user.id,
            categoria="test",
            descripcion="test description"
        )
        
        assert file_upload.id is not None
        assert file_upload.original_filename == "test.csv"
        assert file_upload.categoria == "test"
        assert file_upload.descripcion == "test description"
        assert file_upload.user_id == test_user.id
    
    def test_get_file_upload_by_id(self, db_session, test_user):
        """Test de obtención de archivo por ID."""
        file_repository = FileRepository(db_session)
        
        file_upload = file_repository.create_file_upload(
            original_filename="test.csv",
            s3_key="uploads/test.csv",
            s3_url="https://bucket.s3.amazonaws.com/uploads/test.csv",
            user_id=test_user.id
        )
        
        retrieved = file_repository.get_file_upload_by_id(file_upload.id)
        
        assert retrieved is not None
        assert retrieved.id == file_upload.id
        assert retrieved.original_filename == "test.csv"
    
    def test_update_file_upload_status(self, db_session, test_user):
        """Test de actualización de estado de archivo."""
        file_repository = FileRepository(db_session)
        
        file_upload = file_repository.create_file_upload(
            original_filename="test.csv",
            s3_key="uploads/test.csv",
            s3_url="https://bucket.s3.amazonaws.com/uploads/test.csv",
            user_id=test_user.id,
            status="processing"
        )
        
        updated = file_repository.update_file_upload_status(
            file_upload.id,
            "completed",
            '{"test": "validation"}',
            10
        )
        
        assert updated is not None
        assert updated.status == "completed"
        assert updated.records_count == 10
    
    def test_create_csv_record(self, db_session, test_user):
        """Test de creación de registro CSV."""
        file_repository = FileRepository(db_session)
        
        file_upload = file_repository.create_file_upload(
            original_filename="test.csv",
            s3_key="uploads/test.csv",
            s3_url="https://bucket.s3.amazonaws.com/uploads/test.csv",
            user_id=test_user.id
        )
        
        csv_record = file_repository.create_csv_record(
            file_upload_id=file_upload.id,
            record_data='{"id": 1, "nombre": "Juan"}',
            row_number=2,
            is_valid="true"
        )
        
        assert csv_record.id is not None
        assert csv_record.file_upload_id == file_upload.id
        assert csv_record.row_number == 2
        assert csv_record.is_valid == "true"
    
    def test_get_csv_records_by_file_id(self, db_session, test_user):
        """Test de obtención de registros CSV por archivo."""
        file_repository = FileRepository(db_session)
        
        file_upload = file_repository.create_file_upload(
            original_filename="test.csv",
            s3_key="uploads/test.csv",
            s3_url="https://bucket.s3.amazonaws.com/uploads/test.csv",
            user_id=test_user.id
        )
        
        # Crear varios registros
        for i in range(3):
            file_repository.create_csv_record(
                file_upload_id=file_upload.id,
                record_data=f'{{"id": {i}}}',
                row_number=i+2
            )
        
        records = file_repository.get_csv_records_by_file_id(file_upload.id)
        
        assert len(records) == 3
        assert all(r.file_upload_id == file_upload.id for r in records)

