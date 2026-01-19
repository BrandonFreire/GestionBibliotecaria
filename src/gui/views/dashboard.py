"""
Vista del dashboard principal - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt

from database.connection import DatabaseConnection
from config.settings import Settings


class DashboardView(QWidget):
    """Vista del dashboard con información general."""
    
    def __init__(self, connection: DatabaseConnection):
        super().__init__()
        self.connection = connection
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del dashboard."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Dashboard")
        title.setObjectName("title")
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {Settings.TEXT_COLOR};
        """)
        layout.addWidget(title)
        
        # Panel de conexión
        conn_group = QGroupBox("Estado de Conexión")
        conn_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        conn_layout = QVBoxLayout(conn_group)
        
        self.status_label = QLabel("⚪ No conectado")
        self.status_label.setStyleSheet("font-size: 14pt; padding: 10px;")
        conn_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        test_btn = QPushButton("Probar Conexión")
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Settings.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {Settings.SECONDARY_COLOR};
            }}
        """)
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.clicked.connect(self._test_connection)
        conn_layout.addWidget(test_btn, alignment=Qt.AlignCenter)
        
        layout.addWidget(conn_group)
        
        # Panel de estadísticas
        stats_group = QGroupBox("Estadísticas")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        stats_layout = QVBoxLayout(stats_group)
        
        self.tables_label = QLabel("Tablas: -")
        self.tables_label.setStyleSheet("padding: 10px;")
        stats_layout.addWidget(self.tables_label)
        
        layout.addWidget(stats_group)
        
        # Espaciador
        layout.addStretch()
    
    def _test_connection(self):
        """Prueba la conexión a la base de datos."""
        success, msg = self.connection.test_connection()
        if success:
            self.status_label.setText("🟢 Conectado")
            self.status_label.setStyleSheet(f"font-size: 14pt; padding: 10px; color: {Settings.SUCCESS_COLOR};")
        else:
            self.status_label.setText("🔴 Error de conexión")
            self.status_label.setStyleSheet(f"font-size: 14pt; padding: 10px; color: {Settings.ERROR_COLOR};")
