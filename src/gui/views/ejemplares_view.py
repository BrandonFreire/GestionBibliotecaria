"""
Vista de ejemplares de libros - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt

from config.settings import Settings


class EjemplaresView(QWidget):
    """Vista de ejemplares de libros."""
    
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
        
        title = QLabel("📦 Ejemplares de Libros")
        theme = Settings.get_theme()
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {theme['TEXT_COLOR']};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Botón de nuevo ejemplar
        new_copy_btn = QPushButton("➕ Nuevo Ejemplar")
        new_copy_btn.setStyleSheet(f"""
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
        new_copy_btn.setCursor(Qt.PointingHandCursor)
        new_copy_btn.clicked.connect(self._add_copy)
        header_layout.addWidget(new_copy_btn)
        
        layout.addLayout(header_layout)
        
        # Filtros
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['CARD_BG']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 5, 10, 5)
        
        # Búsqueda
        search_icon = QLabel("🔍")
        filter_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por ISBN o número de ejemplar...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                padding: 8px;
                font-size: 11pt;
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        self.search_input.textChanged.connect(self._filter_copies)
        filter_layout.addWidget(self.search_input, 1)
        
        # Filtro por estado
        status_label = QLabel("Estado:")
        status_label.setStyleSheet(f"color: {theme['TEXT_COLOR']};")
        filter_layout.addWidget(status_label)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Disponible", "Prestado", "En reparación", "Dado de baja"])
        self.status_filter.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                min-width: 130px;
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        self.status_filter.currentTextChanged.connect(self._filter_copies)
        filter_layout.addWidget(self.status_filter)
        
        layout.addWidget(filter_frame)
        
        # Tabla de ejemplares
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ISBN", "Número Ejemplar", "Estado Ejemplar", "Número Estante", "Número Pasillo"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme['CARD_BG']};
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 8px;
                gridline-color: {theme['BORDER_COLOR']};
                color: {theme['TEXT_COLOR']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {Settings.PRIMARY_COLOR};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {theme['USER_FRAME_BG']};
                color: {theme['TEXT_COLOR']};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {theme['BORDER_COLOR']};
                font-weight: bold;
            }}
        """)
        
        layout.addWidget(self.table, 1)
        
        # Estadísticas
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['CARD_BG']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.total_label = QLabel("Total: 0 ejemplares")
        self.total_label.setStyleSheet(f"color: {theme['TEXT_COLOR']};")
        stats_layout.addWidget(self.total_label)
        stats_layout.addStretch()
        
        self.available_label = QLabel("Disponibles: 0")
        self.available_label.setStyleSheet(f"color: {Settings.SUCCESS_COLOR};")
        stats_layout.addWidget(self.available_label)
        
        self.loaned_label = QLabel("Prestados: 0")
        self.loaned_label.setStyleSheet(f"color: {Settings.PRIMARY_COLOR};")
        stats_layout.addWidget(self.loaned_label)
        
        layout.addWidget(stats_frame)
    
    def _load_sample_data(self):
        """Carga datos de ejemplo."""
        # Campos: ISBN, Número Ejemplar, Estado Ejemplar, Número Estante, Número Pasillo
        sample_copies = [
            ("978-0307474728", "1", "Disponible", "1", "A"),
            ("978-0307474728", "2", "Prestado", "1", "A"),
            ("978-0307474728", "3", "Disponible", "1", "A"),
            ("978-0156012195", "1", "Disponible", "2", "A"),
            ("978-0156012195", "2", "Prestado", "2", "A"),
            ("978-0451524935", "1", "En reparación", "1", "B"),
            ("978-0451524935", "2", "Disponible", "1", "B"),
            ("978-0553380163", "1", "Prestado", "2", "B"),
            ("978-1599869773", "1", "Disponible", "1", "C"),
            ("978-0062316097", "1", "Dado de baja", "3", "C"),
        ]
        
        self._populate_table(sample_copies)
    
    def _populate_table(self, copies):
        """Llena la tabla con los ejemplares."""
        self.table.setRowCount(len(copies))
        
        for row, copy in enumerate(copies):
            for col, value in enumerate(copy):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Colorear estado
                if col == 2:  # Estado Ejemplar
                    if value == "Disponible":
                        item.setForeground(Qt.darkGreen)
                    elif value == "Prestado":
                        item.setForeground(Qt.blue)
                    elif value == "En reparación":
                        item.setForeground(Qt.darkYellow)
                    else:  # Dado de baja
                        item.setForeground(Qt.red)
                
                self.table.setItem(row, col, item)
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        available = 0
        loaned = 0
        
        for row in range(total):
            item = self.table.item(row, 2)  # Columna Estado Ejemplar
            if item:
                if item.text() == "Disponible":
                    available += 1
                elif item.text() == "Prestado":
                    loaned += 1
        
        self.total_label.setText(f"Total: {total} ejemplares")
        self.available_label.setText(f"Disponibles: {available}")
        self.loaned_label.setText(f"Prestados: {loaned}")
    
    def _filter_copies(self):
        """Filtra los ejemplares según la búsqueda."""
        search_text = self.search_input.text().lower()
        status = self.status_filter.currentText()
        
        for row in range(self.table.rowCount()):
            show = True
            
            if search_text:
                match = False
                for col in [0, 1]:  # ISBN, Número Ejemplar
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                show = match
            
            if show and status != "Todos":
                status_item = self.table.item(row, 2)  # Estado Ejemplar
                if status_item and status_item.text() != status:
                    show = False
            
            self.table.setRowHidden(row, not show)
    
    def _add_copy(self):
        """Abre el diálogo para agregar ejemplar."""
        QMessageBox.information(
            self,
            "Nuevo Ejemplar",
            "Funcionalidad de agregar ejemplar pendiente de implementar."
        )
