"""
Vista CRUD genérica - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt

from database.connection import DatabaseConnection
from database.queries import QueryManager
from gui.components.tables import DataTable
from config.settings import Settings


class CrudView(QWidget):
    """Vista para operaciones CRUD en tablas."""
    
    def __init__(self, connection: DatabaseConnection):
        super().__init__()
        self.connection = connection
        self.query_manager = QueryManager(connection) if connection.is_connected() else None
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Gestión de Datos")
        title.setObjectName("title")
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {Settings.TEXT_COLOR};
        """)
        layout.addWidget(title)
        
        # Selector de tabla
        select_frame = QFrame()
        select_layout = QHBoxLayout(select_frame)
        select_layout.setContentsMargins(0, 10, 0, 10)
        
        select_layout.addWidget(QLabel("Tabla:"))
        
        self.table_combo = QComboBox()
        self.table_combo.setMinimumWidth(200)
        self.table_combo.currentTextChanged.connect(self._on_table_select)
        select_layout.addWidget(self.table_combo)
        
        load_btn = QPushButton("Cargar")
        load_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Settings.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {Settings.SECONDARY_COLOR};
            }}
        """)
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.clicked.connect(self._load_data)
        select_layout.addWidget(load_btn)
        
        select_layout.addStretch()
        layout.addWidget(select_frame)
        
        # Contenedor para la tabla de datos
        self.data_frame = QFrame()
        self.data_frame.setStyleSheet("background-color: white; border-radius: 4px;")
        self.data_layout = QVBoxLayout(self.data_frame)
        layout.addWidget(self.data_frame, 1)
    
    def _on_table_select(self, text: str):
        """Maneja el cambio de selección de tabla."""
        if text:
            self._load_data()
    
    def _load_data(self):
        """Carga los datos de la tabla seleccionada."""
        if not self.query_manager:
            QMessageBox.warning(self, "Aviso", "No hay conexión activa")
            return
        
        table = self.table_combo.currentText()
        if table:
            try:
                data = self.query_manager.get_table_data(table)
                if data:
                    columns = list(data[0].keys())
                    
                    # Limpiar contenido anterior
                    while self.data_layout.count():
                        child = self.data_layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()
                    
                    # Crear nueva tabla
                    table_widget = DataTable(columns, data)
                    self.data_layout.addWidget(table_widget)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
