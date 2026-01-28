"""
Script de prueba para procedimientos almacenados.
Verifica el funcionamiento de los métodos CRUD de PASILLO, PRESTAMO y USUARIOS.
"""
import sys
import os
from datetime import date, timedelta

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from database.distributed_connection import DistributedConnection
from database.s_p_pasillo import StoredProcedures as SP_Pasillo
from database.s_p_prestamo import SP_Prestamo
from database.s_p_usuarios import SP_Usuarios


def print_separator(title=""):
    """Imprime una línea separadora con título opcional."""
    print("\n" + "=" * 70)
    if title:
        print(f"{title}")
        print("=" * 70)


def test_pasillo(sp_pasillo: SP_Pasillo):
    """Prueba los procedimientos almacenados de PASILLO."""
    print_separator("PRUEBAS DE PASILLO")
    
    # Consultar pasillos existentes
    print("\n1. Consultando pasillos existentes...")
    pasillos = sp_pasillo.consultar_pasillo(node="FIS")
    print(f"   Total de pasillos: {len(pasillos)}")
    if pasillos:
        print(f"   Ejemplo: {pasillos[0]}")
    
    # Consultar pasillos de una biblioteca específica
    print("\n2. Consultando pasillos de biblioteca '01'...")
    pasillos_01 = sp_pasillo.consultar_pasillo(id_biblioteca='01', node="FIS")
    print(f"   Pasillos en biblioteca 01: {len(pasillos_01)}")
    
    print("\n✓ Pruebas de PASILLO completadas")


def test_prestamo(sp_prestamo: SP_Prestamo):
    """Prueba los procedimientos almacenados de PRESTAMO."""
    print_separator("PRUEBAS DE PRESTAMO")
    
    # Consultar préstamos existentes
    print("\n1. Consultando préstamos existentes...")
    prestamos = sp_prestamo.consultar_prestamo(node="FIQA")
    print(f"   Total de préstamos: {len(prestamos)}")
    if prestamos:
        print(f"   Ejemplo: {prestamos[0]}")
    
    # Consultar préstamos activos
    print("\n2. Consultando préstamos activos (no devueltos)...")
    prestamos_activos = sp_prestamo.consultar_prestamos_activos(node="FIQA")
    print(f"   Préstamos activos: {len(prestamos_activos)}")
    
    # Consultar préstamos vencidos
    print("\n3. Consultando préstamos vencidos...")
    prestamos_vencidos = sp_prestamo.consultar_prestamos_vencidos(node="FIQA")
    print(f"   Préstamos vencidos: {len(prestamos_vencidos)}")
    if prestamos_vencidos:
        print(f"   Ejemplo de préstamo vencido:")
        for key, value in list(prestamos_vencidos[0].items())[:5]:
            print(f"     {key}: {value}")
    
    print("\n✓ Pruebas de PRESTAMO completadas")


def test_usuarios(sp_usuarios: SP_Usuarios):
    """Prueba los procedimientos almacenados de USUARIOS."""
    print_separator("PRUEBAS DE USUARIOS")
    
    # Consultar usuarios existentes
    print("\n1. Consultando usuarios existentes...")
    usuarios = sp_usuarios.consultar_usuario(node="FIS")
    print(f"   Total de usuarios: {len(usuarios)}")
    if usuarios:
        print(f"   Ejemplo: {usuarios[0]}")
    
    # Consultar usuarios por biblioteca
    print("\n2. Consultando usuarios de biblioteca '01'...")
    usuarios_01 = sp_usuarios.consultar_usuarios_por_biblioteca('01', node="FIS")
    print(f"   Usuarios en biblioteca 01: {len(usuarios_01)}")
    
    print("\n3. Consultando usuarios de biblioteca '02'...")
    usuarios_02 = sp_usuarios.consultar_usuarios_por_biblioteca('02', node="FIS")
    print(f"   Usuarios en biblioteca 02: {len(usuarios_02)}")
    
    # Buscar usuario por email
    if usuarios:
        email_ejemplo = usuarios[0].get('email_usuario', '')
        if email_ejemplo:
            print(f"\n4. Buscando usuarios con email que contenga '{email_ejemplo[:10]}'...")
            usuarios_email = sp_usuarios.buscar_usuario_por_email(email_ejemplo[:10], node="FIS")
            print(f"   Usuarios encontrados: {len(usuarios_email)}")
    
    print("\n✓ Pruebas de USUARIOS completadas")


def main():
    """Función principal del script de prueba."""
    print_separator("PRUEBA DE PROCEDIMIENTOS ALMACENADOS")
    
    try:
        # Cargar variables de entorno
        load_dotenv()
        print("\n✓ Variables de entorno cargadas")
        
        # Crear conexión distribuida
        print("✓ Inicializando conexiones distribuidas...")
        dist_conn = DistributedConnection()
        
        # Probar conexiones
        print("✓ Probando conexiones a nodos...")
        results = dist_conn.test_all_connections()
        
        all_connected = True
        for node_name, (success, message) in results.items():
            if success:
                print(f"  ✓ Nodo {node_name}: Conectado")
            else:
                print(f"  ✗ Nodo {node_name}: {message}")
                all_connected = False
        
        if not all_connected:
            print("\n⚠️  Algunas conexiones fallaron. Verifica la configuración.")
            return
        
        # Inicializar gestores de procedimientos almacenados
        sp_pasillo = SP_Pasillo(dist_conn)
        sp_prestamo = SP_Prestamo(dist_conn)
        sp_usuarios = SP_Usuarios(dist_conn)
        
        # Ejecutar pruebas
        test_pasillo(sp_pasillo)
        test_prestamo(sp_prestamo)
        test_usuarios(sp_usuarios)
        
        # Cerrar conexiones
        dist_conn.disconnect_all()
        print("\n✓ Conexiones cerradas")
        
        # Resumen final
        print_separator("RESUMEN")
        print("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("\nMódulos de procedimientos almacenados disponibles:")
        print("  • s_p_pasillo.py - CRUD de PASILLO")
        print("  • s_p_prestamo.py - CRUD de PRESTAMO")
        print("  • s_p_usuarios.py - CRUD de USUARIOS")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
