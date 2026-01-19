"""
Configuración de conexión a la base de datos.
"""
import os
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuración para conexión a SQL Server."""
    
    server: str = ""
    database: str = ""
    username: str = ""
    password: str = ""
    driver: str = "ODBC Driver 17 for SQL Server"
    trusted_connection: bool = True
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Crea la configuración desde variables de entorno."""
        return cls(
            server=os.getenv("DB_SERVER", "localhost"),
            database=os.getenv("DB_NAME", ""),
            username=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            driver=os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            trusted_connection=os.getenv("DB_TRUSTED_CONNECTION", "True").lower() == "true"
        )
    
    def get_connection_string(self) -> str:
        """Genera la cadena de conexión para pyodbc."""
        if self.trusted_connection:
            return (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
