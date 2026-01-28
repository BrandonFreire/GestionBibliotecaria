"""
Servicio de autenticación para el sistema.
Maneja login de usuarios a nivel de código.
"""
from typing import Optional, Dict, Tuple
from enum import Enum


class UserRole(Enum):
    """Roles de usuario en el sistema."""
    ADMIN = "admin"
    GESTOR_FIS = "gestor_fis"
    GESTOR_FIQA = "gestor_fiqa"
    USUARIO = "usuario"


class AuthService:
    """Servicio de autenticación de usuarios."""
    
    # Usuarios predefinidos del sistema
    # Formato: username: (password, role, full_name, node)
    USERS = {
        "admin": ("admin123", UserRole.ADMIN, "Administrador del Sistema", "FIS"),
        "gestor_fis": ("fis123", UserRole.GESTOR_FIS, "Gestor FIS", "FIS"),
        "gestor_fiqa": ("fiqa123", UserRole.GESTOR_FIQA, "Gestor FIQA", "FIQA"),
        "usuario": ("user123", UserRole.USUARIO, "Usuario General", "FIS"),
    }
    
    def __init__(self, db_connection=None):
        """
        Inicializa el servicio de autenticación.
        
        Args:
            db_connection: Conexión a la base de datos (opcional, para futuras extensiones).
        """
        self.db_connection = db_connection
        self.current_user: Optional[Dict] = None
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Autentica un usuario.
        
        Args:
            username: Nombre de usuario.
            password: Contraseña del usuario.
        
        Returns:
            Tupla (éxito, datos_usuario, mensaje).
        """
        username = username.strip().lower()
        
        if not username or not password:
            return False, None, "Usuario y contraseña son requeridos"
        
        if username not in self.USERS:
            return False, None, "Usuario no encontrado"
        
        stored_password, role, full_name, node = self.USERS[username]
        
        if password != stored_password:
            return False, None, "Contraseña incorrecta"
        
        # Crear datos del usuario
        user_data = {
            'username': username,
            'full_name': full_name,
            'role': role.value,
            'node': node,
            'permissions': self._get_permissions(role)
        }
        
        self.current_user = user_data
        return True, user_data, "Autenticación exitosa"
    
    def _get_permissions(self, role: UserRole) -> Dict[str, bool]:
        """
        Obtiene los permisos según el rol del usuario.
        
        Args:
            role: Rol del usuario.
        
        Returns:
            Diccionario con permisos.
        """
        if role == UserRole.ADMIN:
            return {
                'can_view_fis': True,
                'can_edit_fis': True,
                'can_view_fiqa': True,
                'can_edit_fiqa': True,
                'can_manage_users': True,
                'can_view_reports': True,
            }
        elif role == UserRole.GESTOR_FIS:
            return {
                'can_view_fis': True,
                'can_edit_fis': True,
                'can_view_fiqa': False,
                'can_edit_fiqa': False,
                'can_manage_users': False,
                'can_view_reports': True,
            }
        elif role == UserRole.GESTOR_FIQA:
            return {
                'can_view_fis': False,
                'can_edit_fis': False,
                'can_view_fiqa': True,
                'can_edit_fiqa': True,
                'can_manage_users': False,
                'can_view_reports': True,
            }
        else:  # USUARIO
            return {
                'can_view_fis': True,
                'can_edit_fis': False,
                'can_view_fiqa': True,
                'can_edit_fiqa': False,
                'can_manage_users': False,
                'can_view_reports': False,
            }
    
    def logout(self):
        """Cierra la sesión del usuario actual."""
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado."""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """Obtiene los datos del usuario actual."""
        return self.current_user
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica si el usuario actual tiene un permiso específico.
        
        Args:
            permission: Nombre del permiso a verificar.
        
        Returns:
            True si tiene el permiso, False en caso contrario.
        """
        if not self.is_authenticated():
            return False
        
        return self.current_user.get('permissions', {}).get(permission, False)
    
    @staticmethod
    def get_available_users() -> Dict[str, Dict[str, str]]:
        """
        Obtiene información de los usuarios disponibles (para documentación).
        
        Returns:
            Diccionario con información de usuarios.
        """
        return {
            username: {
                'role': role.value,
                'full_name': full_name,
                'node': node
            }
            for username, (_, role, full_name, node) in AuthService.USERS.items()
        }
