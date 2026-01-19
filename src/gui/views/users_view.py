"""
Vista de usuarios registrados - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt

from config.settings import Settings


class UsersView(QWidget):
    """Vista de usuarios registrados."""
    
    def __init__(self, db_connection=None):
        super().__init__()
        self.db_connection = db_connection
        self._create_widgets()
        self._load_sample_data()
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("👥 Usuarios Registrados")
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {Settings.TEXT_COLOR};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Botón de nuevo usuario
        new_user_btn = QPushButton("➕ Nuevo Usuario")
        new_user_btn.setStyleSheet(f"""
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
        new_user_btn.setCursor(Qt.PointingHandCursor)
        new_user_btn.clicked.connect(self._add_user)
        header_layout.addWidget(new_user_btn)
        
        layout.addLayout(header_layout)
        
        # Barra de búsqueda
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        search_icon = QLabel("🔍")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar usuario por nombre o email...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 8px;
                font-size: 11pt;
            }
        """)
        self.search_input.textChanged.connect(self._filter_users)
        search_layout.addWidget(self.search_input, 1)
        
        layout.addWidget(search_frame)
        
        # Tabla de usuarios
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Email", "Tipo", "Estado", "Préstamos Activos"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.table.doubleClicked.connect(self._show_user_details)
        
        layout.addWidget(self.table, 1)
        
        # Estadísticas
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.total_label = QLabel("Total: 0 usuarios")
        stats_layout.addWidget(self.total_label)
        stats_layout.addStretch()
        self.active_label = QLabel("Activos: 0")
        self.active_label.setStyleSheet(f"color: {Settings.SUCCESS_COLOR};")
        stats_layout.addWidget(self.active_label)
        
        layout.addWidget(stats_frame)
    
    def _load_sample_data(self):
        """Carga datos de ejemplo."""
        sample_users = [
            (1, "Juan Pérez", "juan.perez@email.com", "Estudiante", "Activo", 2),
            (2, "María García", "maria.garcia@email.com", "Profesor", "Activo", 1),
            (3, "Carlos López", "carlos.lopez@email.com", "Estudiante", "Activo", 0),
            (4, "Ana Martínez", "ana.martinez@email.com", "Estudiante", "Suspendido", 3),
            (5, "Pedro Sánchez", "pedro.sanchez@email.com", "Profesor", "Activo", 0),
            (6, "Laura Torres", "laura.torres@email.com", "Estudiante", "Activo", 1),
        ]
        
        self._populate_table(sample_users)
    
    def _populate_table(self, users):
        """Llena la tabla con los usuarios."""
        self.table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            for col, value in enumerate(user):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter if col in [0, 5] else Qt.AlignLeft | Qt.AlignVCenter)
                
                # Colorear estado
                if col == 4:
                    if value == "Activo":
                        item.setForeground(Qt.darkGreen)
                    else:
                        item.setForeground(Qt.red)
                
                self.table.setItem(row, col, item)
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        active = 0
        for row in range(total):
            item = self.table.item(row, 4)
            if item and item.text() == "Activo":
                active += 1
        
        self.total_label.setText(f"Total: {total} usuarios")
        self.active_label.setText(f"Activos: {active}")
    
    def _filter_users(self):
        """Filtra los usuarios según la búsqueda."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show = True
            
            if search_text:
                match = False
                for col in [1, 2]:  # Nombre, Email
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                show = match
            
            self.table.setRowHidden(row, not show)
    
    def _add_user(self):
        """Abre el diálogo para agregar usuario."""
        QMessageBox.information(
            self,
            "Nuevo Usuario",
            "Funcionalidad de agregar usuario pendiente de implementar."
        )
    
    def _show_user_details(self, index):
        """Muestra los detalles del usuario."""
        row = index.row()
        user_info = f"""
        <b>ID:</b> {self.table.item(row, 0).text()}<br>
        <b>Nombre:</b> {self.table.item(row, 1).text()}<br>
        <b>Email:</b> {self.table.item(row, 2).text()}<br>
        <b>Tipo:</b> {self.table.item(row, 3).text()}<br>
        <b>Estado:</b> {self.table.item(row, 4).text()}<br>
        <b>Préstamos Activos:</b> {self.table.item(row, 5).text()}
        """
        
        QMessageBox.information(self, "Detalles del Usuario", user_info)
