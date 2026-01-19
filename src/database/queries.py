"""
Gestión de consultas SQL.
"""
from typing import List, Dict, Any, Optional
from .connection import DatabaseConnection


class QueryManager:
    """Clase para gestionar consultas SQL comunes."""
    
    def __init__(self, connection: DatabaseConnection):
        """
        Inicializa el gestor de consultas.
        
        Args:
            connection: Conexión a la base de datos.
        """
        self.connection = connection
    
    def get_all_tables(self) -> List[str]:
        """Obtiene todas las tablas de la base de datos."""
        query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """
        results = self.connection.execute_query(query)
        return [row['TABLE_NAME'] for row in results]
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Obtiene las columnas de una tabla específica."""
        query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """
        return self.connection.execute_query(query, (table_name,))
    
    def get_table_data(
        self, 
        table_name: str, 
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Obtiene los datos de una tabla con paginación."""
        # Nota: Usar parámetros con cuidado para evitar SQL injection
        query = f"""
            SELECT * FROM [{table_name}]
            ORDER BY (SELECT NULL)
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        """
        return self.connection.execute_query(query, (offset, limit))
    
    def count_table_rows(self, table_name: str) -> int:
        """Cuenta el número de filas en una tabla."""
        query = f"SELECT COUNT(*) FROM [{table_name}]"
        return self.connection.execute_scalar(query) or 0
    
    def insert_record(
        self, 
        table_name: str, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Inserta un registro en una tabla.
        
        Args:
            table_name: Nombre de la tabla.
            data: Diccionario con columnas y valores.
        
        Returns:
            True si se insertó correctamente.
        """
        columns = ', '.join([f'[{col}]' for col in data.keys()])
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO [{table_name}] ({columns}) VALUES ({placeholders})"
        
        rows_affected = self.connection.execute_non_query(
            query, 
            tuple(data.values())
        )
        return rows_affected > 0
    
    def update_record(
        self,
        table_name: str,
        data: Dict[str, Any],
        where_column: str,
        where_value: Any
    ) -> bool:
        """
        Actualiza un registro en una tabla.
        
        Args:
            table_name: Nombre de la tabla.
            data: Diccionario con columnas y valores a actualizar.
            where_column: Columna para la condición WHERE.
            where_value: Valor para la condición WHERE.
        
        Returns:
            True si se actualizó correctamente.
        """
        set_clause = ', '.join([f'[{col}] = ?' for col in data.keys()])
        query = f"UPDATE [{table_name}] SET {set_clause} WHERE [{where_column}] = ?"
        
        params = tuple(data.values()) + (where_value,)
        rows_affected = self.connection.execute_non_query(query, params)
        return rows_affected > 0
    
    def delete_record(
        self,
        table_name: str,
        where_column: str,
        where_value: Any
    ) -> bool:
        """
        Elimina un registro de una tabla.
        
        Args:
            table_name: Nombre de la tabla.
            where_column: Columna para la condición WHERE.
            where_value: Valor para la condición WHERE.
        
        Returns:
            True si se eliminó correctamente.
        """
        query = f"DELETE FROM [{table_name}] WHERE [{where_column}] = ?"
        rows_affected = self.connection.execute_non_query(query, (where_value,))
        return rows_affected > 0
