"""
Gestión de conexiones a SQL Server.
"""
import pyodbc
from typing import Optional, List, Any, Dict
from contextlib import contextmanager

from config.database import DatabaseConfig


class DatabaseConnection:
    """Clase para gestionar conexiones a SQL Server."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Inicializa la conexión con la configuración proporcionada.
        
        Args:
            config: Configuración de la base de datos. Si es None, 
                   se carga desde variables de entorno.
        """
        self.config = config or DatabaseConfig.from_env()
        self._connection: Optional[pyodbc.Connection] = None
    
    def connect(self) -> bool:
        """
        Establece la conexión a la base de datos.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            connection_string = self.config.get_connection_string()
            self._connection = pyodbc.connect(connection_string)
            return True
        except pyodbc.Error as e:
            print(f"Error de conexión: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión a la base de datos."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def is_connected(self) -> bool:
        """Verifica si hay una conexión activa."""
        return self._connection is not None
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager para obtener un cursor.
        
        Yields:
            Cursor de la conexión.
        """
        if not self._connection:
            raise ConnectionError("No hay conexión activa a la base de datos")
        
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT y devuelve los resultados.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
        
        Returns:
            Lista de diccionarios con los resultados.
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
    
    def execute_non_query(self, query: str, params: tuple = ()) -> int:
        """
        Ejecuta una consulta INSERT, UPDATE o DELETE.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
        
        Returns:
            Número de filas afectadas.
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            self._connection.commit()
            return cursor.rowcount
    
    def execute_stored_procedure(self, query: str, params: tuple = ()) -> int:
        """
        Ejecuta un stored procedure sin transacciones explícitas de Python.
        El SP maneja sus propias transacciones en SQL Server.
        
        Args:
            query: Query del stored procedure a ejecutar.
            params: Parámetros para el SP.
        
        Returns:
            Número de filas afectadas.
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            # Hacer commit después de ejecutar el SP
            self._connection.commit()
            return cursor.rowcount
    
    def execute_scalar(self, query: str, params: tuple = ()) -> Any:
        """
        Ejecuta una consulta y devuelve un único valor.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
        
        Returns:
            Primer valor del primer resultado.
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row[0] if row else None
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Prueba la conexión a la base de datos.
        
        Returns:
            Tupla (éxito, mensaje).
        """
        try:
            if self.connect():
                # Ejecutar una consulta simple para verificar
                version = self.execute_scalar("SELECT @@VERSION")
                self.disconnect()
                return True, f"Conexión exitosa. SQL Server: {version[:50]}..."
            return False, "No se pudo establecer la conexión"
        except Exception as e:
            return False, f"Error: {str(e)}"
