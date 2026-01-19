"""
Pruebas para el módulo de base de datos.
"""
import unittest
from src.config.database import DatabaseConfig


class TestDatabaseConfig(unittest.TestCase):
    """Pruebas para DatabaseConfig."""
    
    def test_trusted_connection_string(self):
        """Prueba cadena de conexión con autenticación Windows."""
        config = DatabaseConfig(
            server="localhost",
            database="TestDB",
            trusted_connection=True
        )
        conn_str = config.get_connection_string()
        self.assertIn("Trusted_Connection=yes", conn_str)
        self.assertIn("SERVER=localhost", conn_str)
    
    def test_sql_auth_connection_string(self):
        """Prueba cadena de conexión con autenticación SQL."""
        config = DatabaseConfig(
            server="localhost",
            database="TestDB",
            username="user",
            password="pass",
            trusted_connection=False
        )
        conn_str = config.get_connection_string()
        self.assertIn("UID=user", conn_str)
        self.assertIn("PWD=pass", conn_str)


if __name__ == '__main__':
    unittest.main()
