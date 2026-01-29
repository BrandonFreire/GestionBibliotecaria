"""
Gestión de conexiones distribuidas a SQL Server.
Maneja conexiones a múltiples nodos (FIS y FIQA).
"""
import pyodbc
from typing import Optional, List, Any, Dict
from contextlib import contextmanager

from config.database import DistributedDatabaseConfig, DatabaseConfig
from database.connection import DatabaseConnection


class DistributedConnection:
    """Clase para gestionar conexiones a múltiples nodos de SQL Server."""
    
    def __init__(self, config: Optional[DistributedDatabaseConfig] = None):
        """
        Inicializa las conexiones distribuidas.
        
        Args:
            config: Configuración de la base de datos distribuida. 
                   Si es None, se carga desde variables de entorno.
        """
        self.config = config or DistributedDatabaseConfig.from_env()
        self._connections: Dict[str, DatabaseConnection] = {}
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Inicializa las conexiones para cada nodo."""
        for node_name, node_config in self.config.get_all_nodes().items():
            self._connections[node_name] = DatabaseConnection(node_config)
    
    def connect_node(self, node_name: str) -> bool:
        """
        Conecta a un nodo específico.
        
        Args:
            node_name: Nombre del nodo (FIS o FIQA).
            
        Returns:
            True si la conexión fue exitosa, False en caso contrario.
        """
        node_name = node_name.upper()
        if node_name not in self._connections:
            print(f"Nodo '{node_name}' no encontrado en la configuración")
            return False
        
        return self._connections[node_name].connect()
    
    def connect_all(self) -> Dict[str, bool]:
        """
        Intenta conectar a todos los nodos.
        
        Returns:
            Diccionario con el estado de conexión de cada nodo.
        """
        results = {}
        for node_name in self._connections.keys():
            results[node_name] = self.connect_node(node_name)
        return results
    
    def disconnect_node(self, node_name: str):
        """Desconecta de un nodo específico."""
        node_name = node_name.upper()
        if node_name in self._connections:
            self._connections[node_name].disconnect()
    
    def disconnect_all(self):
        """Desconecta de todos los nodos."""
        for connection in self._connections.values():
            connection.disconnect()
    
    def get_connection(self, node_name: str) -> Optional[DatabaseConnection]:
        """
        Obtiene la conexión a un nodo específico.
        
        Args:
            node_name: Nombre del nodo (FIS o FIQA).
            
        Returns:
            Objeto DatabaseConnection o None si no existe.
        """
        return self._connections.get(node_name.upper())
    
    def execute_query(self, node_name: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT en un nodo específico.
        
        Args:
            node_name: Nombre del nodo donde ejecutar la consulta.
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
        
        Returns:
            Lista de diccionarios con los resultados.
        """
        connection = self.get_connection(node_name)
        if not connection:
            raise ValueError(f"Nodo '{node_name}' no encontrado")
        
        if not connection.is_connected():
            if not connection.connect():
                raise ConnectionError(f"No se pudo conectar al nodo '{node_name}'")
        
        return connection.execute_query(query, params)
    
    def execute_non_query(self, node_name: str, query: str, params: tuple = ()) -> int:
        """
        Ejecuta una consulta INSERT, UPDATE o DELETE en un nodo específico.
        
        Args:
            node_name: Nombre del nodo donde ejecutar la consulta.
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
        
        Returns:
            Número de filas afectadas.
        """
        connection = self.get_connection(node_name)
        if not connection:
            raise ValueError(f"Nodo '{node_name}' no encontrado")
        
        if not connection.is_connected():
            if not connection.connect():
                raise ConnectionError(f"No se pudo conectar al nodo '{node_name}'")
        
        return connection.execute_non_query(query, params)
    
    def test_all_connections(self) -> Dict[str, tuple[bool, str]]:
        """
        Prueba la conexión a todos los nodos.
        
        Returns:
            Diccionario con el resultado de la prueba para cada nodo.
        """
        results = {}
        for node_name, connection in self._connections.items():
            results[node_name] = connection.test_connection()
        return results
    
    def get_node_info(self, node_name: str) -> Optional[Dict[str, str]]:
        """
        Obtiene información sobre un nodo específico.
        
        Args:
            node_name: Nombre del nodo.
            
        Returns:
            Diccionario con información del nodo.
        """
        node_config = self.config.get_node_config(node_name)
        if not node_config:
            return None
        
        return {
            'name': node_name.upper(),
            'server': node_config.server,
            'database': node_config.database,
            'port': str(node_config.port),
            'is_primary': node_name.upper() == self.config.primary_node
        }
    
    def get_all_nodes_info(self) -> List[Dict[str, str]]:
        """
        Obtiene información de todos los nodos.
        
        Returns:
            Lista de diccionarios con información de cada nodo.
        """
        return [
            self.get_node_info(node_name) 
            for node_name in self._connections.keys()
        ]
