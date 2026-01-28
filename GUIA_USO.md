# Guía de Uso del Sistema

## 📋 Usuarios Predefinidos

El sistema incluye los siguientes usuarios para pruebas:

| Usuario | Contraseña | Rol | Nodo | Permisos |
|---------|------------|-----|------|----------|
| `admin` | `admin123` | Administrador | FIS | Acceso completo a ambos nodos |
| `gestor_fis` | `fis123` | Gestor FIS | FIS | Solo nodo FIS (lectura/escritura) |
| `gestor_fiqa` | `fiqa123` | Gestor FIQA | FIQA | Solo nodo FIQA (lectura/escritura) |
| `usuario` | `user123` | Usuario | FIS | Solo lectura en ambos nodos |

## 🔧 Configuración de Conexión

Las credenciales de la base de datos están configuradas en el archivo `.env`:

```env
# Nodo FIS (Gestión)
DB_FIS_SERVER=26.176.70.167
DB_FIS_NAME=FIS
DB_FIS_USER=sa
DB_FIS_PASSWORD=P@ssw0rd

# Nodo FIQA
DB_FIQA_SERVER=26.202.221.168
DB_FIQA_NAME=FIQA
DB_FIQA_USER=sa
DB_FIQA_PASSWORD=P@ssw0rd
```

## 🚀 Cómo Ejecutar

### 1. Probar Conexión a la Base de Datos

Antes de ejecutar la aplicación, prueba la conexión:

```bash
python scripts\test_connection.py
```

Este script verificará:
- ✅ Conexión al nodo FIS
- ✅ Conexión al nodo FIQA
- ✅ Sistema de autenticación

### 2. Ejecutar la Aplicación

```bash
python run.py
```

### 3. Iniciar Sesión

1. Ingresa uno de los usuarios predefinidos
2. La interfaz se adaptará según el nodo del usuario
3. Los permisos se aplicarán automáticamente

## 🔐 Sistema de Permisos

### Administrador (`admin`)
- ✅ Ver y editar datos en FIS
- ✅ Ver y editar datos en FIQA
- ✅ Gestionar usuarios
- ✅ Ver reportes

### Gestor FIS (`gestor_fis`)
- ✅ Ver y editar datos en FIS
- ❌ Acceso a FIQA
- ❌ Gestionar usuarios
- ✅ Ver reportes

### Gestor FIQA (`gestor_fiqa`)
- ❌ Acceso a FIS
- ✅ Ver y editar datos en FIQA
- ❌ Gestionar usuarios
- ✅ Ver reportes

### Usuario (`usuario`)
- ✅ Ver datos en FIS (solo lectura)
- ✅ Ver datos en FIQA (solo lectura)
- ❌ Editar datos
- ❌ Gestionar usuarios
- ❌ Ver reportes

## 📝 Notas Importantes

1. **Radmin VPN**: Asegúrate de que Radmin VPN esté conectado antes de ejecutar la aplicación
2. **SQL Server**: Ambos servidores SQL Server deben estar en ejecución
3. **Firewall**: Verifica que el puerto 1433 esté abierto en ambos nodos
4. **Credenciales**: Si cambias las credenciales de SQL Server, actualiza el archivo `.env`

## 🛠️ Solución de Problemas

### Error de conexión a nodo FIS o FIQA

1. Verifica que Radmin VPN esté conectado
2. Haz ping a las IPs: `ping 26.176.70.167` y `ping 26.202.221.168`
3. Verifica que SQL Server esté en ejecución en ambos nodos
4. Verifica las credenciales en `.env`

### Error de autenticación

1. Verifica que estés usando uno de los usuarios predefinidos
2. Las contraseñas son case-sensitive
3. Los nombres de usuario deben estar en minúsculas

### La interfaz no se adapta al nodo

1. Verifica que el usuario tenga asignado el nodo correcto
2. Revisa el archivo `auth_service.py` para confirmar la configuración
