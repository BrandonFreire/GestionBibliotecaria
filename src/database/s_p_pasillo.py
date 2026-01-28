"""
Gestión de llamadas a procedimientos almacenados.
Este módulo proporciona una interfaz Python para ejecutar los procedimientos
almacenados CRUD de las tablas PASILLO, PRESTAMO y USUARIOS.
"""
from typing import List, Dict, Any, Optional
from .distributed_connection import DistributedConnection


class StoredProcedures:
    """Gestiona llamadas a procedimientos almacenados en la base de datos distribuida."""
    
    def __init__(self, dist_conn: DistributedConnection):
        """
        Inicializa el gestor de procedimientos almacenados.
        
        Args:
            dist_conn: Conexión distribuida a los nodos FIS y FIQA.
        """
        self.dist_conn = dist_conn
    
    # ==================== PASILLO ====================
    
    def insertar_pasillo(self, id_biblioteca: str, num_pasillo: int, 
                         node: str = "FIS") -> bool:
        """
        Inserta un nuevo pasillo en la base de datos.
        
        Args:
            id_biblioteca: ID de la biblioteca ('01' para FIS, '02' para FIQA).
            num_pasillo: Número del pasillo.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se insertó correctamente, False en caso contrario.
        """
        query = "EXEC sp_Insertar_Pasillo @id_biblioteca=?, @num_pasillo=?"
        try:
            self.dist_conn.execute_non_query(node, query, (id_biblioteca, num_pasillo))
            return True
        except Exception as e:
            print(f"Error al insertar pasillo: {e}")
            return False
    
    def actualizar_pasillo(self, id_biblioteca: str, num_pasillo_actual: int,
                          num_pasillo_nuevo: int, node: str = "FIS") -> bool:
        """
        Actualiza el número de un pasillo.
        
        Args:
            id_biblioteca: ID de la biblioteca.
            num_pasillo_actual: Número actual del pasillo.
            num_pasillo_nuevo: Nuevo número del pasillo.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Actualizar_Pasillo 
                   @id_biblioteca=?, 
                   @num_pasillo_actual=?, 
                   @num_pasillo_nuevo=?"""
        try:
            self.dist_conn.execute_non_query(
                node, query, 
                (id_biblioteca, num_pasillo_actual, num_pasillo_nuevo)
            )
            return True
        except Exception as e:
            print(f"Error al actualizar pasillo: {e}")
            return False
    
    def eliminar_pasillo(self, id_biblioteca: str, num_pasillo: int,
                        node: str = "FIS") -> bool:
        """
        Elimina un pasillo de la base de datos.
        
        Args:
            id_biblioteca: ID de la biblioteca.
            num_pasillo: Número del pasillo a eliminar.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        query = "EXEC sp_Eliminar_Pasillo @id_biblioteca=?, @num_pasillo=?"
        try:
            self.dist_conn.execute_non_query(node, query, (id_biblioteca, num_pasillo))
            return True
        except Exception as e:
            print(f"Error al eliminar pasillo: {e}")
            return False
    
    def consultar_pasillo(self, id_biblioteca: Optional[str] = None,
                         node: str = "FIS") -> List[Dict[str, Any]]:
        """
        Consulta pasillos de la base de datos.
        
        Args:
            id_biblioteca: ID de la biblioteca (opcional). Si es None, devuelve todos.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            Lista de diccionarios con los datos de los pasillos.
        """
        if id_biblioteca is None:
            query = "EXEC sp_Consultar_Pasillo"
            params = ()
        else:
            query = "EXEC sp_Consultar_Pasillo @id_biblioteca=?"
            params = (id_biblioteca,)
        
        try:
            return self.dist_conn.execute_query(node, query, params)
        except Exception as e:
            print(f"Error al consultar pasillos: {e}")
            return []
