"""
Gestión de llamadas a procedimientos almacenados de PRESTAMO.
Este módulo proporciona una interfaz Python para ejecutar los procedimientos
almacenados CRUD de la tabla PRESTAMO.
"""
from typing import List, Dict, Any, Optional
from datetime import date
from .distributed_connection import DistributedConnection


class SP_Prestamo:
    """Gestiona llamadas a procedimientos almacenados de PRESTAMO."""
    
    def __init__(self, dist_conn: DistributedConnection):
        """
        Inicializa el gestor de procedimientos almacenados de PRESTAMO.
        
        Args:
            dist_conn: Conexión distribuida a los nodos FIS y FIQA.
        """
        self.dist_conn = dist_conn
    
    def insertar_prestamo(self, 
                         id_biblioteca: str,
                         ISBN: str,
                         id_ejemplar: int,
                         cedula: str,
                         fecha_prestamo: date,
                         fecha_devolucion_tope: date,
                         node: str = "FIS") -> bool:
        """
        Inserta un nuevo préstamo en la base de datos.
        
        Args:
            id_biblioteca: ID de la biblioteca ('01' para FIS, '02' para FIQA).
            ISBN: ISBN del libro.
            id_ejemplar: ID del ejemplar.
            cedula: Cédula del usuario.
            fecha_prestamo: Fecha en que se realiza el préstamo.
            fecha_devolucion_tope: Fecha tope para devolver el libro.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se insertó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Insertar_Prestamo 
                   @id_biblioteca=?, 
                   @ISBN=?, 
                   @id_ejemplar=?, 
                   @cedula=?, 
                   @fecha_prestamo=?, 
                   @fecha_devolucion_tope=?"""
        try:
            self.dist_conn.execute_non_query(
                node, query, 
                (id_biblioteca, ISBN, id_ejemplar, cedula, 
                 fecha_prestamo, fecha_devolucion_tope)
            )
            print(f"Préstamo registrado exitosamente en nodo {node}")
            return True
        except Exception as e:
            print(f"Error al insertar préstamo: {e}")
            return False
    
    def actualizar_prestamo(self,
                           id_biblioteca: str,
                           ISBN: str,
                           id_ejemplar: int,
                           cedula: str,
                           fecha_prestamo: date,
                           fecha_devolucion_nueva: date,
                           node: str = "FIS") -> bool:
        """
        Actualiza un préstamo registrando la devolución del libro.
        
        Args:
            id_biblioteca: ID de la biblioteca.
            ISBN: ISBN del libro.
            id_ejemplar: ID del ejemplar.
            cedula: Cédula del usuario.
            fecha_prestamo: Fecha original del préstamo.
            fecha_devolucion_nueva: Fecha real en que se devolvió el libro.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Actualizar_Prestamo 
                   @id_biblioteca=?, 
                   @ISBN=?, 
                   @id_ejemplar=?, 
                   @cedula=?, 
                   @fecha_prestamo=?, 
                   @fecha_devolucion_nueva=?"""
        try:
            self.dist_conn.execute_stored_procedure(
                node, query,
                (id_biblioteca, ISBN, id_ejemplar, cedula, 
                 fecha_prestamo, fecha_devolucion_nueva)
            )
            print(f"Devolución registrada correctamente en nodo {node}")
            return True
        except Exception as e:
            print(f"Error al actualizar préstamo: {e}")
            return False
    
    def eliminar_prestamo(self,
                         id_biblioteca: str,
                         ISBN: str,
                         id_ejemplar: int,
                         cedula: str,
                         fecha_prestamo: date,
                         node: str = "FIS") -> bool:
        """
        Elimina un registro de préstamo de la base de datos.
        
        Args:
            id_biblioteca: ID de la biblioteca.
            ISBN: ISBN del libro.
            id_ejemplar: ID del ejemplar.
            cedula: Cédula del usuario.
            fecha_prestamo: Fecha del préstamo.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Eliminar_Prestamo 
                   @id_biblioteca=?, 
                   @ISBN=?, 
                   @id_ejemplar=?, 
                   @cedula=?, 
                   @fecha_prestamo=?"""
        try:
            self.dist_conn.execute_non_query(
                node, query,
                (id_biblioteca, ISBN, id_ejemplar, cedula, fecha_prestamo)
            )
            print(f"Préstamo eliminado correctamente en nodo {node}")
            return True
        except Exception as e:
            print(f"Error al eliminar préstamo: {e}")
            return False
    
    def consultar_prestamo(self, 
                          id_biblioteca: Optional[str] = None,
                          node: str = "FIS") -> List[Dict[str, Any]]:
        """
        Consulta préstamos de la base de datos.
        
        Args:
            id_biblioteca: ID de la biblioteca (opcional). Si es None, devuelve todos.
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            Lista de diccionarios con los datos de los préstamos.
        """
        if id_biblioteca is None:
            query = "EXEC sp_Consultar_Prestamo"
            params = ()
        else:
            query = "EXEC sp_Consultar_Prestamo @id_biblioteca=?"
            params = (id_biblioteca,)
        
        try:
            return self.dist_conn.execute_query(node, query, params)
        except Exception as e:
            print(f"Error al consultar préstamos: {e}")
            return []
    
    def consultar_prestamos_activos(self, node: str = "FIS") -> List[Dict[str, Any]]:
        """
        Consulta préstamos activos (no devueltos).
        
        Args:
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            Lista de préstamos activos (fecha_devolucion IS NULL).
        """
        query = "SELECT * FROM v_Prestamo WHERE fecha_devolucion IS NULL"
        try:
            return self.dist_conn.execute_query(node, query)
        except Exception as e:
            print(f"Error al consultar préstamos activos: {e}")
            return []
    
    def consultar_prestamos_vencidos(self, node: str = "FIS") -> List[Dict[str, Any]]:
        """
        Consulta préstamos vencidos (pasaron la fecha tope y no se devolvieron).
        
        Args:
            node: Nodo donde ejecutar (por defecto FIS).
        
        Returns:
            Lista de préstamos vencidos.
        """
        query = """SELECT * FROM v_Prestamo 
                   WHERE fecha_devolucion IS NULL 
                   AND fecha_devolucion_tope < GETDATE()"""
        try:
            return self.dist_conn.execute_query(node, query)
        except Exception as e:
            print(f"Error al consultar préstamos vencidos: {e}")
            return []
