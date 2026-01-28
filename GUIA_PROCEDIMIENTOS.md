# Guía de Uso de Procedimientos Almacenados

## 📚 Módulos Implementados

Se han creado tres módulos para gestionar los procedimientos almacenados CRUD:

### 1. `s_p_pasillo.py` - Gestión de Pasillos
### 2. `s_p_prestamo.py` - Gestión de Préstamos  
### 3. `s_p_usuarios.py` - Gestión de Usuarios

---

## 🔧 Uso Básico

### Inicialización

```python
from database.distributed_connection import DistributedConnection
from database.s_p_pasillo import StoredProcedures as SP_Pasillo
from database.s_p_prestamo import SP_Prestamo
from database.s_p_usuarios import SP_Usuarios

# Crear conexión distribuida
dist_conn = DistributedConnection()

# Inicializar gestores
sp_pasillo = SP_Pasillo(dist_conn)
sp_prestamo = SP_Prestamo(dist_conn)
sp_usuarios = SP_Usuarios(dist_conn)
```

---

## 📋 PASILLO - Métodos Disponibles

### Insertar Pasillo
```python
sp_pasillo.insertar_pasillo(
    id_biblioteca='01',
    num_pasillo=105,
    node='FIS'
)
```

### Actualizar Pasillo
```python
sp_pasillo.actualizar_pasillo(
    id_biblioteca='01',
    num_pasillo_actual=105,
    num_pasillo_nuevo=106,
    node='FIS'
)
```

### Eliminar Pasillo
```python
sp_pasillo.eliminar_pasillo(
    id_biblioteca='01',
    num_pasillo=106,
    node='FIS'
)
```

### Consultar Pasillos
```python
# Todos los pasillos
pasillos = sp_pasillo.consultar_pasillo(node='FIS')

# Pasillos de una biblioteca específica
pasillos_01 = sp_pasillo.consultar_pasillo(id_biblioteca='01', node='FIS')
```

---

## 📚 PRESTAMO - Métodos Disponibles

### Insertar Préstamo
```python
from datetime import date, timedelta

sp_prestamo.insertar_prestamo(
    id_biblioteca='01',
    ISBN='978-0073511245',
    id_ejemplar=1,
    cedula='1700000001',
    fecha_prestamo=date.today(),
    fecha_devolucion_tope=date.today() + timedelta(days=15),
    node='FIQA'
)
```

### Actualizar Préstamo (Registrar Devolución)
```python
sp_prestamo.actualizar_prestamo(
    id_biblioteca='01',
    ISBN='978-0073511245',
    id_ejemplar=1,
    cedula='1700000001',
    fecha_prestamo=date(2024, 1, 15),
    fecha_devolucion_nueva=date.today(),
    node='FIQA'
)
```

### Eliminar Préstamo
```python
sp_prestamo.eliminar_prestamo(
    id_biblioteca='01',
    ISBN='978-0073511245',
    id_ejemplar=1,
    cedula='1700000001',
    fecha_prestamo=date(2024, 1, 15),
    node='FIQA'
)
```

### Consultar Préstamos
```python
# Todos los préstamos
prestamos = sp_prestamo.consultar_prestamo(node='FIQA')

# Préstamos de una biblioteca
prestamos_01 = sp_prestamo.consultar_prestamo(id_biblioteca='01', node='FIQA')

# Préstamos activos (no devueltos)
activos = sp_prestamo.consultar_prestamos_activos(node='FIQA')

# Préstamos vencidos
vencidos = sp_prestamo.consultar_prestamos_vencidos(node='FIQA')
```

---

## 👥 USUARIOS - Métodos Disponibles

### Insertar Usuario
```python
sp_usuarios.insertar_usuario(
    id_biblioteca='01',
    cedula='1700000099',
    nombre_usuario='Juan',
    apellido_usuario='Pérez',
    email_usuario='juan.perez@example.com',
    celular_usuario='0987654321',
    node='FIS'
)
```

### Actualizar Usuario
```python
sp_usuarios.actualizar_usuario(
    id_biblioteca='01',
    cedula='1700000099',
    nombre_usuario='Juan Carlos',
    apellido_usuario='Pérez García',
    email_usuario='juancarlos.perez@example.com',
    celular_usuario='0987654322',
    node='FIS'
)
```

### Eliminar Usuario
```python
sp_usuarios.eliminar_usuario(
    id_biblioteca='01',
    cedula='1700000099',
    node='FIS'
)
```

### Consultar Usuarios
```python
# Todos los usuarios
usuarios = sp_usuarios.consultar_usuario(node='FIS')

# Usuario específico por cédula
usuario = sp_usuarios.consultar_usuario(cedula='1700000001', node='FIS')

# Usuarios por biblioteca
usuarios_01 = sp_usuarios.consultar_usuarios_por_biblioteca('01', node='FIS')
usuarios_02 = sp_usuarios.consultar_usuarios_por_biblioteca('02', node='FIS')

# Buscar por email
usuarios = sp_usuarios.buscar_usuario_por_email('example.com', node='FIS')
```

---

## 🧪 Ejecutar Pruebas

Para probar todos los procedimientos almacenados:

```bash
.\.venv\Scripts\python.exe scripts\test_stored_procedures.py
```

Este script verificará:
- ✅ Conexión a los nodos
- ✅ Consulta de pasillos
- ✅ Consulta de préstamos (todos, activos, vencidos)
- ✅ Consulta de usuarios (todos, por biblioteca, por email)

---

## 📝 Notas Importantes

### Nodos por Defecto

- **PASILLO**: Por defecto usa nodo `FIS`
- **PRESTAMO**: Por defecto usa nodo `FIQA`
- **USUARIOS**: Por defecto usa nodo `FIS`

Puedes cambiar el nodo especificando el parámetro `node` en cualquier método.

### Fragmentación de USUARIOS

Los usuarios tienen **fragmentación mixta**:
- **Vertical**: Contacto (email, celular) siempre en FIS
- **Horizontal**: Info (nombre, apellido) en FIS ('01') o FIQA ('02')

El procedimiento almacenado maneja esto automáticamente.

### Manejo de Errores

Todos los métodos retornan:
- `True` si la operación fue exitosa
- `False` si hubo un error
- Lista de diccionarios para consultas

Los errores se imprimen en consola.

---

## 🎯 Ejemplo Completo

```python
from dotenv import load_dotenv
from database.distributed_connection import DistributedConnection
from database.s_p_usuarios import SP_Usuarios
from datetime import date

# Cargar configuración
load_dotenv()

# Conectar
dist_conn = DistributedConnection()
sp_usuarios = SP_Usuarios(dist_conn)

# Consultar usuarios
usuarios = sp_usuarios.consultar_usuario(node='FIS')
print(f"Total usuarios: {len(usuarios)}")

# Buscar usuario específico
usuario = sp_usuarios.consultar_usuario(cedula='1700000001', node='FIS')
if usuario:
    print(f"Usuario encontrado: {usuario[0]['nombre_usuario']}")

# Cerrar conexión
dist_conn.disconnect_all()
```
