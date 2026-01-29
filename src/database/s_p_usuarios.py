"""
Gestión de llamadas a procedimientos almacenados de USUARIOS.
Este módulo proporciona una interfaz Python para ejecutar los procedimientos
almacenados CRUD de la tabla USUARIOS (fragmentación mixta).
"""
from typing import List, Dict, Any, Optional
from .distributed_connection import DistributedConnection


class SP_Usuarios:
    """Gestiona llamadas a procedimientos almacenados de USUARIOS."""
    
    def __init__(self, dist_conn: DistributedConnection):
        """
        Inicializa el gestor de procedimientos almacenados de USUARIOS.
        
        Args:
            dist_conn: Conexión distribuida a los nodos FIS y FIQA.
        """
        self.dist_conn = dist_conn
    
    def insertar_usuario(self,
                        id_biblioteca: str,
                        cedula: str,
                        nombre_usuario: str,
                        apellido_usuario: str,
                        email_usuario: str,
                        celular_usuario: str,
                        node: str = "FIS") -> bool:
        """
        Inserta un nuevo usuario en la base de datos.
        
        Este procedimiento maneja la fragmentación mixta:
        - Contacto (vertical): Siempre en FIS
        - Info (horizontal): En FIS ('01') o FIQA ('02') según id_biblioteca
        
        Args:
            id_biblioteca: ID de la biblioteca ('01' para FIS, '02' para FIQA).
            cedula: Cédula del usuario.
            nombre_usuario: Nombre del usuario.
            apellido_usuario: Apellido del usuario.
            email_usuario: Email del usuario.
            celular_usuario: Celular del usuario.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se insertó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Insertar_Usuario 
                   @id_biblioteca=?, 
                   @cedula=?, 
                   @nombre_usuario=?, 
                   @apellido_usuario=?, 
                   @email_usuario=?, 
                   @celular_usuario=?"""
        try:
            self.dist_conn.execute_non_query(
                node, query,
                (id_biblioteca, cedula, nombre_usuario, apellido_usuario,
                 email_usuario, celular_usuario)
            )
            print(f"Usuario registrado correctamente en nodo {node} (Fragmentación Mixta)")
            return True
        except Exception as e:
            print(f"Error al insertar usuario: {e}")
            return False
    
    def actualizar_usuario(self,
                          id_biblioteca: str,
                          cedula: str,
                          nombre_usuario: str,
                          apellido_usuario: str,
                          email_usuario: str,
                          celular_usuario: str,
                          node: str = "FIS") -> bool:
        """
        Actualiza los datos de un usuario.
        
        Actualiza ambas partes:
        - Contacto (vertical): Email y celular
        - Info (horizontal): Nombre y apellido
        
        Args:
            id_biblioteca: ID de la biblioteca.
            cedula: Cédula del usuario.
            nombre_usuario: Nuevo nombre del usuario.
            apellido_usuario: Nuevo apellido del usuario.
            email_usuario: Nuevo email del usuario.
            celular_usuario: Nuevo celular del usuario.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Actualizar_Usuario 
                   @id_biblioteca=?, 
                   @cedula=?, 
                   @nombre_usuario=?, 
                   @apellido_usuario=?, 
                   @email_usuario=?, 
                   @celular_usuario=?"""
        try:
            self.dist_conn.execute_non_query(
                node, query,
                (id_biblioteca, cedula, nombre_usuario, apellido_usuario,
                 email_usuario, celular_usuario)
            )
            print(f"Datos de usuario actualizados en nodo {node}")
            return True
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return False
    
    def eliminar_usuario(self,
                        id_biblioteca: str,
                        cedula: str,
                        node: str = "FIS") -> bool:
        """
        Elimina un usuario de la base de datos.
        
        Elimina de ambas tablas:
        1. Info (horizontal): Según la biblioteca
        2. Contacto (vertical): Si ya no existe en ninguna horizontal
        
        Args:
            id_biblioteca: ID de la biblioteca.
            cedula: Cédula del usuario a eliminar.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Eliminar_Usuario 
                   @id_biblioteca=?, 
                   @cedula=?"""
        try:
            self.dist_conn.execute_non_query(node, query, (id_biblioteca, cedula))
            print(f"Usuario eliminado del sistema en nodo {node}")
            return True
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False
    
    def consultar_usuario(self,
                         cedula: Optional[str] = None,
                         node: str = "FIS") -> List[Dict[str, Any]]:
        """
        Consulta usuarios de la base de datos usando la vista.
        
        La vista v_Usuario une automáticamente los datos de:
        - Usuario_contacto (vertical)
        - Usuarios_info_01 y Usuarios_info_02 (horizontal)
        
        Args:
            cedula: Cédula del usuario (opcional). Si es None, devuelve todos.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            Lista de diccionarios con los datos de los usuarios.
        """
        if cedula is None:
            query = "EXEC sp_Consultar_Usuario"
            params = ()
        else:
            query = "EXEC sp_Consultar_Usuario @cedula=?"
            params = (cedula,)
        
        try:
            return self.dist_conn.execute_query(node, query, params)
        except Exception as e:
            print(f"Error al consultar usuarios: {e}")
            return []