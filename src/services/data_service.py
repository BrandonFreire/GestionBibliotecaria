"""
Servicio de datos - Capa de lógica de negocio.
"""
from typing import List, Dict, Any, Optional
from database.connection import DatabaseConnection
from database.queries import QueryManager


class DataService:
    """Servicio para operaciones de datos."""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.query_manager = QueryManager(connection)
    
    def get_tables(self) -> List[str]:
        """Obtiene lista de tablas."""
        return self.query_manager.get_all_tables()
    
    def get_table_info(self, table: str) -> Dict[str, Any]:
        """Obtiene información de una tabla."""
        columns = self.query_manager.get_table_columns(table)
        count = self.query_manager.count_table_rows(table)
        return {'columns': columns, 'row_count': count}
    
    def fetch_data(self, table: str, limit: int = 100) -> List[Dict]:
        """Obtiene datos de una tabla."""
        return self.query_manager.get_table_data(table, limit)
    
    def create_record(self, table: str, data: Dict) -> bool:
        """Crea un registro."""
        return self.query_manager.insert_record(table, data)
    
    def update_record(self, table: str, data: Dict, pk_col: str, pk_val) -> bool:
        """Actualiza un registro."""
        return self.query_manager.update_record(table, data, pk_col, pk_val)
    
    def delete_record(self, table: str, pk_col: str, pk_val) -> bool:
        """Elimina un registro."""
        return self.query_manager.delete_record(table, pk_col, pk_val)
