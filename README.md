# Proyecto de Bases de Datos Distribuidas

Aplicación con interfaz gráfica para gestión de bases de datos distribuidas usando Python y SQL Server.

## 📁 Estructura del Proyecto

```
proyecto_bd_distribuidas/
├── src/                          # Código fuente principal
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada de la aplicación
│   ├── config/                   # Configuración de la aplicación
│   │   ├── __init__.py
│   │   ├── database.py           # Configuración de conexiones BD
│   │   └── settings.py           # Configuración general
│   ├── database/                 # Capa de acceso a datos
│   │   ├── __init__.py
│   │   ├── connection.py         # Gestión de conexiones SQL Server
│   │   ├── queries.py            # Consultas SQL
│   │   └── models.py             # Modelos de datos
│   ├── gui/                      # Interfaz gráfica
│   │   ├── __init__.py
│   │   ├── main_window.py        # Ventana principal
│   │   ├── components/           # Componentes reutilizables
│   │   │   ├── __init__.py
│   │   │   ├── tables.py         # Tablas/grids de datos
│   │   │   ├── forms.py          # Formularios
│   │   │   └── dialogs.py        # Diálogos/popups
│   │   └── views/                # Vistas específicas
│   │       ├── __init__.py
│   │       ├── dashboard.py      # Vista principal/dashboard
│   │       └── crud_view.py      # Vista para operaciones CRUD
│   ├── services/                 # Lógica de negocio
│   │   ├── __init__.py
│   │   └── data_service.py       # Servicios de datos
│   └── utils/                    # Utilidades generales
│       ├── __init__.py
│       ├── helpers.py            # Funciones auxiliares
│       └── validators.py         # Validaciones
├── tests/                        # Pruebas unitarias
│   ├── __init__.py
│   ├── test_database.py
│   └── test_services.py
├── scripts/                      # Scripts SQL y utilidades
│   └── create_tables.sql         # Script de creación de tablas
├── docs/                         # Documentación
│   └── setup.md                  # Guía de instalación
├── .env.example                  # Ejemplo de variables de entorno
├── requirements.txt              # Dependencias del proyecto
├── README.md                     # Este archivo
└── run.py                        # Script para ejecutar la aplicación
```

## 🛠️ Tecnologías

- **Python 3.10+**
- **Tkinter** - Interfaz gráfica (incluido en Python)
- **pyodbc** - Conexión a SQL Server
- **python-dotenv** - Manejo de variables de entorno

## ⚙️ Instalación

1. Clonar el repositorio o descargar los archivos

2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   ```bash
   copy .env.example .env
   # Editar .env con tus credenciales de SQL Server
   ```

5. Ejecutar la aplicación:
   ```bash
   python run.py
   ```

## 🔗 Configuración de SQL Server

Asegúrate de tener:
- SQL Server instalado y en ejecución
- SSMS (SQL Server Management Studio) configurado
- Las credenciales de acceso a tu base de datos

## 📝 Uso

[Instrucciones de uso de la aplicación]

## 👥 Autor

[Tu nombre]
