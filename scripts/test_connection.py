"""
Script de prueba de conexión a la base de datos distribuida.
Verifica la conectividad a los nodos FIS y FIQA.
"""
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from database.distributed_connection import DistributedConnection
from services.auth_service import AuthService


def print_separator():
    """Imprime una línea separadora."""
    print("=" * 70)


def test_database_connections():
    """Prueba las conexiones a los nodos de la base de datos."""
    print_separator()
    print("PRUEBA DE CONEXIÓN A BASE DE DATOS DISTRIBUIDA")
    print_separator()
    
    # Cargar variables de entorno
    load_dotenv()
    print("\n✓ Variables de entorno cargadas desde .env")
    
    # Crear conexión distribuida
    print("\nInicializando conexiones distribuidas...")
    dist_conn = DistributedConnection()
    
    # Mostrar información de nodos
    print("\nInformación de nodos configurados:")
    for node_info in dist_conn.get_all_nodes_info():
        print(f"\n  Nodo: {node_info['name']}")
        print(f"  Servidor: {node_info['server']}")
        print(f"  Base de datos: {node_info['database']}")
        print(f"  Puerto: {node_info['port']}")
        print(f"  Nodo gestion: {'Sí' if node_info['is_primary'] else 'No'}")
    
    # Probar conexiones
    print("\n" + "=" * 70)
    print("PROBANDO CONEXIONES A NODOS")
    print_separator()
    
    results = dist_conn.test_all_connections()
    
    for node_name, (success, message) in results.items():
        print(f"\nNodo {node_name}:")
        if success:
            print(f"  ✅ CONEXIÓN EXITOSA")
            print(f"  {message}")
        else:
            print(f"  ❌ CONEXIÓN FALLIDA")
            print(f"  Error: {message}")
    
    # Cerrar conexiones
    dist_conn.disconnect_all()
    print("\n✓ Conexiones cerradas")
    
    return results


def test_authentication():
    """Prueba el sistema de autenticación."""
    print("\n" + "=" * 70)
    print("PRUEBA DE SISTEMA DE AUTENTICACIÓN")
    print_separator()
    
    auth_service = AuthService()
    
    # Mostrar usuarios disponibles
    print("\nUsuarios disponibles:")
    users = AuthService.get_available_users()
    for username, info in users.items():
        print(f"\n  Usuario: {username}")
        print(f"  Nombre: {info['full_name']}")
        print(f"  Rol: {info['role']}")
        print(f"  Nodo: {info['node']}")
    
    # Probar autenticación
    print("\n" + "=" * 70)
    print("PROBANDO AUTENTICACIÓN")
    print_separator()
    
    test_cases = [
        ("admin", "admin123", True),
        ("gestor_fis", "fis123", True),
        ("usuario", "wrongpass", False),
    ]
    
    for username, password, should_succeed in test_cases:
        print(f"\n🔐 Probando: {username} / {'*' * len(password)}")
        success, user_data, message = auth_service.authenticate(username, password)
        
        if success:
            print(f"  ✅ {message}")
            print(f"  Usuario: {user_data['full_name']}")
            print(f"  Rol: {user_data['role']}")
            print(f"  Nodo: {user_data['node']}")
            auth_service.logout()
        else:
            print(f"  ❌ {message}")


def main():
    """Función principal del script de prueba."""
    try:
        # Probar conexiones a base de datos
        db_results = test_database_connections()
        
        # Probar autenticación
        test_authentication()
        
        # Resumen final
        print("\n" + "=" * 70)
        print("RESUMEN DE PRUEBAS")
        print_separator()
        
        all_success = all(success for success, _ in db_results.values())
        
        if all_success:
            print("\nTODAS LAS PRUEBAS PASARON EXITOSAMENTE")
            print("\nEl sistema está listo para usar")
            print("\nPuedes ejecutar la aplicación con: python run.py")
        else:
            print("\nALGUNAS CONEXIONES FALLARON")
            print("\nVerifica:")
            print("  1. Que los servidores SQL Server estén en ejecución")
            print("  2. Que Radmin VPN esté conectado")
            print("  3. Que las credenciales en .env sean correctas")
            print("  4. Que el firewall permita las conexiones")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
