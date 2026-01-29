"""
Gestión de llamadas a procedimientos almacenados de LIBRO.
Este módulo proporciona una interfaz Python para ejecutar los procedimientos
almacenados CRUD de la tabla LIBRO (replicación transaccional).

Nota: LIBRO usa replicación transaccional, no fragmentación.
- FIS es el publicador (escrituras aquí)
- FIQA es el suscriptor (recibe réplica automática)
"""
from typing import List, Dict, Any, Optional
from .distributed_connection import DistributedConnection


class SP_Libro:
    """Gestiona llamadas a procedimientos almacenados de LIBRO."""
    
    def __init__(self, dist_conn: DistributedConnection):
        """
        Inicializa el gestor de procedimientos almacenados.
        
        Args:
            dist_conn: Conexión distribuida a los nodos FIS y FIQA.
        """
        self.dist_conn = dist_conn
    
    def insertar_libro(self, ISBN: str, nombre_libro: str, anio_edicion: int,
                       categoria_libro: str, lugar_impresion_libro: str,
                       node: str = "FIS") -> bool:
        """
        Inserta un nuevo libro en la base de datos.
        En replicación transaccional, siempre escribir en FIS (publicador).
        
        Args:
            ISBN: Código ISBN del libro.
            nombre_libro: Nombre/título del libro.
            anio_edicion: Año de edición.
            categoria_libro: Categoría del libro.
            lugar_impresion_libro: Lugar de impresión.
            node: Nodo donde ejecutar (siempre FIS para escrituras).
        
        Returns:
            True si se insertó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Insertar_Libro 
                   @ISBN=?, 
                   @nombre_libro=?, 
                   @anio_edicion=?, 
                   @categoria_libro=?, 
                   @lugar_impresion_libro=?"""
        try:
            self.dist_conn.execute_non_query(
                node, query, 
                (ISBN, nombre_libro, anio_edicion, categoria_libro, lugar_impresion_libro)
            )
            return True
        except Exception as e:
            print(f"Error al insertar libro: {e}")
            return False
    
    def actualizar_libro(self, ISBN: str, nombre_libro: str, anio_edicion: int,
                         categoria_libro: str, lugar_impresion_libro: str,
                         node: str = "FIS") -> bool:
        """
        Actualiza un libro existente.
        En replicación transaccional, siempre escribir en FIS (publicador).
        
        Args:
            ISBN: Código ISBN del libro (clave primaria, no se modifica).
            nombre_libro: Nuevo nombre/título del libro.
            anio_edicion: Nuevo año de edición.
            categoria_libro: Nueva categoría del libro.
            lugar_impresion_libro: Nuevo lugar de impresión.
            node: Nodo donde ejecutar (siempre FIS para escrituras).
        
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        query = """EXEC sp_Actualizar_Libro 
                   @ISBN=?, 
                   @nombre_libro=?, 
                   @anio_edicion=?, 
                   @categoria_libro=?, 
                   @lugar_impresion_libro=?"""
        try:
            self.dist_conn.execute_non_query(
                node, query, 
                (ISBN, nombre_libro, anio_edicion, categoria_libro, lugar_impresion_libro)
            )
            return True
        except Exception as e:
            print(f"Error al actualizar libro: {e}")
            return False
    
    def eliminar_libro(self, ISBN: str, node: str = "FIS") -> bool:
        """
        Elimina un libro de la base de datos.
        En replicación transaccional, siempre escribir en FIS (publicador).
        
        Args:
            ISBN: Código ISBN del libro a eliminar.
            node: Nodo donde ejecutar (siempre FIS para escrituras).
        
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        query = "EXEC sp_Eliminar_Libro @ISBN=?"
        try:
            self.dist_conn.execute_non_query(node, query, (ISBN,))
            return True
        except Exception as e:
            print(f"Error al eliminar libro: {e}")
            return False
    
    def consultar_libro(self, ISBN: Optional[str] = None,
                        node: str = "FIS") -> List[Dict[str, Any]]:
        """
        Consulta libros de la base de datos.
        Puede leer desde FIS o FIQA (ambos tienen los mismos datos).
        
        Args:
            ISBN: ISBN del libro (opcional). Si es None, devuelve todos.
            node: Nodo donde ejecutar (FIS o FIQA, ambos válidos para lectura).
        
        Returns:
            Lista de diccionarios con los datos de los libros.
        """
        if ISBN is None:
            query = "EXEC sp_Consultar_Libro"
            params = ()
        else:
            query = "EXEC sp_Consultar_Libro @ISBN=?"
            params = (ISBN,)
        
        try:
            return self.dist_conn.execute_query(node, query, params)
        except Exception as e:
            print(f"Error al consultar libros: {e}")
            return []
