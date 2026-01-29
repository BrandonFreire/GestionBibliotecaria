"""
Módulo de base de datos.
"""
from .connection import DatabaseConnection
from .distributed_connection import DistributedConnection

__all__ = ['DatabaseConnection', 'DistributedConnection']
