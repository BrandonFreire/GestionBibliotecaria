# scripts/query_tables.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from database.distributed_connection import DistributedConnection

load_dotenv()

# Crear conexión
dist_conn = DistributedConnection()

# Consultar tabla LIBRO en nodo FIS
print("=== LIBROS (tabla replicada) ===")
try:
    libros = dist_conn.execute_query("FIS", "SELECT * FROM LIBRO")
    for i, libro in enumerate(libros):
        print(f"{i+1}. {libro}")
except Exception as e:
    print(f"Error: {e}")

# Consultar tabla BIBLIOTECA en nodo FIS mediante la VISTA
print("\n=== BIBLIOTECAS EN NODO FIS ===")
try:
    bibliotecas = dist_conn.execute_query("FIS", "SELECT * FROM v_Biblioteca")
    for i, biblioteca in enumerate(bibliotecas):
        print(f"{i+1}. {biblioteca}")
except Exception as e:
    print(f"Error: {e}")

# Consultar tabla PASILLO en nodo FIS mediante la VISTA
print("\n=== PASILLOS EN NODO FIS ===")
try:
    pasillos = dist_conn.execute_query("FIS", "SELECT * FROM v_Pasillo")
    for i, pasillo in enumerate(pasillos):
        print(f"{i+1}. {pasillo}")
except Exception as e:
    print(f"Error: {e}")

# Consultar tabla PRESTAMO en nodo FIS mediante la VISTA
print("\n=== PRESTAMOS EN NODO FIS ===")
try:
    prestamos = dist_conn.execute_query("FIS", "SELECT * FROM v_Prestamo")
    for i, prestamo in enumerate(prestamos):
        print(f"{i+1}. {prestamo}")
except Exception as e:
    print(f"Error: {e}")

# Consultar tabla USUARIOS en nodo FIS mediante la VISTA
print("\n=== USUARIOS EN NODO FIS ===")
try:
    usuarios = dist_conn.execute_query("FIS", "SELECT * FROM v_Usuario")
    for i, usuario in enumerate(usuarios):
        print(f"{i+1}. {usuario}")
except Exception as e:
    print(f"Error: {e}")

dist_conn.disconnect_all()