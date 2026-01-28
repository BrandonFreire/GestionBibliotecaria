"""
Configuración de conexión a la base de datos distribuida.
"""
import os
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class DatabaseConfig:
    """Configuración para conexión a SQL Server."""
    
    server: str = ""
    database: str = ""
    username: str = ""
    password: str = ""
    driver: str = "ODBC Driver 17 for SQL Server"
    trusted_connection: bool = True
    port: int = 1433
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Crea la configuración desde variables de entorno."""
        return cls(
            server=os.getenv("DB_SERVER", "localhost"),
            database=os.getenv("DB_NAME", ""),
            username=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            driver=os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            trusted_connection=os.getenv("DB_TRUSTED_CONNECTION", "True").lower() == "true",
            port=int(os.getenv("DB_PORT", "1433"))
        )
    
    def get_connection_string(self) -> str:
        """Genera la cadena de conexión para pyodbc."""
        server_with_port = f"{self.server},{self.port}" if self.port != 1433 else self.server
        
        if self.trusted_connection:
            return (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={server_with_port};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={server_with_port};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )


@dataclass
class DistributedDatabaseConfig:
    """Configuración para base de datos distribuida con múltiples nodos."""
    
    nodes: Dict[str, DatabaseConfig]
    primary_node: str = "FIS"
    
    @classmethod
    def from_env(cls) -> "DistributedDatabaseConfig":
        """Crea la configuración distribuida con credenciales directas."""
        nodes = {}
        
        # Configuración del nodo FIS (WIN-PHDDNKD39M9 - Nodo 1)
        nodes["FIS"] = DatabaseConfig(
            server="WIN-PHDDNKD39M9",
            database="FIS",
            username="sa",
            password="P@ssw0rd",
            driver="ODBC Driver 17 for SQL Server",
            trusted_connection=False,
            port=1433
        )
        
        # Configuración del nodo FIQA (Slim - Nodo 2)
        nodes["FIQA"] = DatabaseConfig(
            server="Slim",
            database="FIQA",
            username="sa",
            password="P@ssw0rd",
            driver="ODBC Driver 17 for SQL Server",
            trusted_connection=False,
            port=1433
        )
        
        primary_node = "FIS"
        
        return cls(nodes=nodes, primary_node=primary_node)
    
    def get_node_config(self, node_name: str) -> Optional[DatabaseConfig]:
        """Obtiene la configuración de un nodo específico."""
        return self.nodes.get(node_name.upper())
    
    def get_primary_config(self) -> DatabaseConfig:
        """Obtiene la configuración del nodo primario."""
        return self.nodes[self.primary_node]
    
    def get_all_nodes(self) -> Dict[str, DatabaseConfig]:
        """Obtiene todas las configuraciones de nodos."""
        return self.nodes
