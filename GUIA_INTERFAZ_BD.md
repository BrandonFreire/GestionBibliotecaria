# Guía: Cómo Poblar Tablas en la Interfaz Gráfica

## 🎯 Arquitectura Recomendada (SIN DAO/DTO)

Tu arquitectura actual es **correcta y suficiente**:

```
┌─────────────────────────────────────────┐
│   Vista (PyQt5)                         │
│   - usuarios_view.py                    │
│   - prestamos_view.py                   │
│   - pasillos_view.py                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Procedimientos Almacenados (DAOs)     │
│   - s_p_usuarios.py                     │
│   - s_p_prestamo.py                     │
│   - s_p_pasillo.py                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Conexión Distribuida                  │
│   - distributed_connection.py           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   SQL Server (FIS y FIQA)               │
│   - Procedimientos Almacenados          │
│   - Vistas                              │
└─────────────────────────────────────────┘
```

**¿Por qué NO necesitas DAO/DTO?**

- ✅ **Los módulos `s_p_*.py` YA SON tus DAOs** (Data Access Objects)
- ✅ **Los diccionarios de Python funcionan como DTOs** (Data Transfer Objects)
- ✅ **Los procedimientos almacenados manejan la lógica de negocio**
- ❌ **Agregar más capas = código innecesario y complejo**

---

## 📊 Patrón para Poblar Tablas

### 1. Estructura de la Vista

```python
from database.distributed_connection import DistributedConnection
from database.s_p_usuarios import SP_Usuarios  # O el módulo correspondiente

class MiVista(QWidget):
    def __init__(self, dist_conn: DistributedConnection = None):
        super().__init__()
        
        # Conexión a la BD
        self.dist_conn = dist_conn or DistributedConnection()
        self.sp = SP_Usuarios(self.dist_conn)  # Módulo de procedimientos
        
        self._create_widgets()
        self.load_data()  # Cargar datos al iniciar
```

### 2. Método para Cargar Datos

```python
def load_data(self):
    """Carga los datos desde la base de datos."""
    try:
        # Llamar al procedimiento almacenado
        datos = self.sp.consultar_usuario(node="FIS")
        
        if datos:
            self._populate_table(datos)
        else:
            QMessageBox.warning(self, "Sin Datos", "No hay registros.")
            
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Error al cargar: {str(e)}")
```

### 3. Método para Poblar la Tabla

```python
def _populate_table(self, datos):
    """Llena la tabla con los datos de la BD."""
    self.table.setRowCount(len(datos))
    
    for row, registro in enumerate(datos):
        # Extraer valores del diccionario
        columns = [
            registro.get('campo1', ''),
            registro.get('campo2', ''),
            registro.get('campo3', ''),
        ]
        
        for col, value in enumerate(columns):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col, item)
    
    self._update_stats()
```

---

## 📋 Ejemplos por Vista

### USUARIOS (Ya implementado)

```python
# En usuarios_view.py
from database.s_p_usuarios import SP_Usuarios

def load_data(self):
    usuarios = self.sp_usuarios.consultar_usuario(node="FIS")
    self._populate_table(usuarios)
```

### PRÉSTAMOS

```python
# En prestamos_view.py
from database.s_p_prestamo import SP_Prestamo

class PrestamosView(QWidget):
    def __init__(self, dist_conn=None):
        super().__init__()
        self.dist_conn = dist_conn or DistributedConnection()
        self.sp_prestamo = SP_Prestamo(self.dist_conn)
        self._create_widgets()
        self.load_data()
    
    def load_data(self):
        """Carga préstamos desde la BD."""
        try:
            # Obtener todos los préstamos
            prestamos = self.sp_prestamo.consultar_prestamo(node="FIQA")
            self._populate_table(prestamos)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def _populate_table(self, prestamos):
        """Llena la tabla de préstamos."""
        self.table.setRowCount(len(prestamos))
        
        for row, prestamo in enumerate(prestamos):
            columns = [
                prestamo.get('id_biblioteca', ''),
                prestamo.get('ISBN', ''),
                prestamo.get('id_ejemplar', ''),
                prestamo.get('cedula', ''),
                prestamo.get('fecha_prestamo', ''),
                prestamo.get('fecha_devolucion_tope', ''),
                prestamo.get('fecha_devolucion', '') or 'Pendiente'
            ]
            
            for col, value in enumerate(columns):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
```

### PASILLOS

```python
# En pasillos_view.py (si existe)
from database.s_p_pasillo import StoredProcedures as SP_Pasillo

class PasillosView(QWidget):
    def __init__(self, dist_conn=None):
        super().__init__()
        self.dist_conn = dist_conn or DistributedConnection()
        self.sp_pasillo = SP_Pasillo(self.dist_conn)
        self._create_widgets()
        self.load_data()
    
    def load_data(self):
        """Carga pasillos desde la BD."""
        try:
            pasillos = self.sp_pasillo.consultar_pasillo(node="FIS")
            self._populate_table(pasillos)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def _populate_table(self, pasillos):
        """Llena la tabla de pasillos."""
        self.table.setRowCount(len(pasillos))
        
        for row, pasillo in enumerate(pasillos):
            columns = [
                pasillo.get('id_biblioteca', ''),
                pasillo.get('num_pasillo', '')
            ]
            
            for col, value in enumerate(columns):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
```

---

## 🔄 Operaciones CRUD Completas

### Insertar (Create)

```python
def _add_user(self):
    """Agregar nuevo usuario."""
    # Mostrar diálogo para capturar datos
    # (puedes usar QDialog personalizado)
    
    success = self.sp_usuarios.insertar_usuario(
        id_biblioteca='01',
        cedula='1700000099',
        nombre_usuario='Juan',
        apellido_usuario='Pérez',
        email_usuario='juan@example.com',
        celular_usuario='0987654321',
        node='FIS'
    )
    
    if success:
        QMessageBox.information(self, "Éxito", "Usuario agregado")
        self.load_data()  # Recargar tabla
    else:
        QMessageBox.critical(self, "Error", "No se pudo agregar")
```

### Actualizar (Update)

```python
def _edit_user(self):
    """Editar usuario seleccionado."""
    row = self.table.currentRow()
    if row < 0:
        QMessageBox.warning(self, "Advertencia", "Seleccione un usuario")
        return
    
    # Obtener datos actuales
    cedula = self.table.item(row, 1).text()
    
    # Mostrar diálogo con datos actuales
    # Capturar nuevos valores
    
    success = self.sp_usuarios.actualizar_usuario(
        id_biblioteca='01',
        cedula=cedula,
        nombre_usuario='Nuevo Nombre',
        apellido_usuario='Nuevo Apellido',
        email_usuario='nuevo@example.com',
        celular_usuario='0999999999',
        node='FIS'
    )
    
    if success:
        QMessageBox.information(self, "Éxito", "Usuario actualizado")
        self.load_data()
    else:
        QMessageBox.critical(self, "Error", "No se pudo actualizar")
```

### Eliminar (Delete)

```python
def _delete_user(self):
    """Eliminar usuario seleccionado."""
    row = self.table.currentRow()
    if row < 0:
        QMessageBox.warning(self, "Advertencia", "Seleccione un usuario")
        return
    
    cedula = self.table.item(row, 1).text()
    id_biblioteca = self.table.item(row, 0).text()
    
    # Confirmar eliminación
    reply = QMessageBox.question(
        self, 
        "Confirmar",
        f"¿Eliminar usuario {cedula}?",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        success = self.sp_usuarios.eliminar_usuario(
            id_biblioteca=id_biblioteca,
            cedula=cedula,
            node='FIS'
        )
        
        if success:
            QMessageBox.information(self, "Éxito", "Usuario eliminado")
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", "No se pudo eliminar")
```

---

## 🎨 Botones de Acción

Agrega botones para las operaciones CRUD:

```python
# En _create_widgets()

# Botón Refrescar
refresh_btn = QPushButton("🔄 Refrescar")
refresh_btn.clicked.connect(self.load_data)

# Botón Agregar
add_btn = QPushButton("➕ Nuevo")
add_btn.clicked.connect(self._add_user)

# Botón Editar
edit_btn = QPushButton("✏️ Editar")
edit_btn.clicked.connect(self._edit_user)

# Botón Eliminar
delete_btn = QPushButton("🗑️ Eliminar")
delete_btn.clicked.connect(self._delete_user)
```

---

## 📝 Resumen

### ✅ LO QUE DEBES HACER:

1. **Importar el módulo de procedimientos almacenados** en cada vista
2. **Inicializar la conexión** en `__init__`
3. **Llamar a `load_data()`** para cargar datos desde la BD
4. **Usar `_populate_table()`** para llenar la tabla con los datos
5. **Implementar CRUD** usando los métodos de `s_p_*.py`

### ❌ LO QUE NO NECESITAS:

1. **DAO adicionales** - Ya los tienes en `s_p_*.py`
2. **DTO/Modelos** - Los diccionarios funcionan perfectamente
3. **ORM** - Los procedimientos almacenados son más eficientes
4. **Capas extras** - Mantén la arquitectura simple

---

## 🚀 Próximos Pasos

1. **Actualiza `prestamos_view.py`** siguiendo el patrón de `usuarios_view.py`
2. **Actualiza `libros_view.py`** (si tienes procedimientos para libros)
3. **Crea diálogos** para agregar/editar registros
4. **Prueba las operaciones CRUD** en cada vista

¿Necesitas ayuda para implementar alguna vista específica?
