# Guía de Instalación

## Requisitos Previos

1. **Python 3.10+** - [Descargar](https://www.python.org/downloads/)
2. **SQL Server** - Con una base de datos configurada
3. **ODBC Driver 17 for SQL Server** - [Descargar](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Pasos de Instalación

### 1. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
copy .env.example .env
```
Edita `.env` con tus credenciales de SQL Server.

### 4. Ejecutar la aplicación
```bash
python run.py
```

## Solución de Problemas

- **Error de conexión**: Verifica que SQL Server esté corriendo y las credenciales sean correctas.
- **Error de driver ODBC**: Asegúrate de tener instalado el driver ODBC 17.
