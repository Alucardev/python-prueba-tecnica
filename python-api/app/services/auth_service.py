"""
Servicio de Autenticación.
Maneja la lógica de negocio relacionada con autenticación y JWT.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.auth import TokenData


class AuthService:
    """Servicio para operaciones de autenticación."""
    
    def __init__(self, user_repository: UserRepository):
        """
        Inicializa el servicio con un repositorio de usuario.
        
        Args:
            user_repository: Repositorio de usuario
        """
        self.user_repository = user_repository
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Autentica un usuario verificando sus credenciales.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario autenticado o None si las credenciales son inválidas
        """
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
        
        if not self.user_repository.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def create_access_token(self, user: User) -> str:
        """
        Crea un token JWT para un usuario.
        
        Args:
            user: Usuario para el cual crear el token
            
        Returns:
            Token JWT firmado
        """
        # Tiempo de expiración: 15 minutos
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        
        # Datos a incluir en el token
        # Obtener el nombre del rol desde la relación
        role_name = user.role_obj.name if user.role_obj else "user"
        to_encode = {
            "id_usuario": user.id,
            "rol": role_name,
            "exp": expire
        }
        
        # Crear y firmar el token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verifica y decodifica un token JWT.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Datos del token o None si es inválido o ha expirado
        """
        try:
            # Decodificar el token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Extraer los datos
            id_usuario: int = payload.get("id_usuario")
            rol: str = payload.get("rol")
            exp: Optional[datetime] = datetime.fromtimestamp(payload.get("exp"))
            
            if id_usuario is None or rol is None:
                return None
            
            return TokenData(id_usuario=id_usuario, rol=rol, exp=exp)
            
        except JWTError:
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Renueva un token JWT generando uno nuevo con tiempo de expiración adicional.
        
        Args:
            token: Token JWT original
            
        Returns:
            Nuevo token JWT o None si el token original es inválido o ha expirado
        """
        # Verificar el token original
        token_data = self.verify_token(token)
        if not token_data:
            return None
        
        # Obtener el usuario
        user = self.user_repository.get_by_id(token_data.id_usuario)
        if not user:
            return None
        
        # Crear un nuevo token con el mismo usuario y rol
        return self.create_access_token(user)

