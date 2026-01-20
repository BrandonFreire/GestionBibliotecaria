"""
Vista de historial de préstamos - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt

from config.settings import Settings


class PrestamosView(QWidget):
    """Vista de historial de préstamos."""
    
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
        
        title = QLabel("📋 Historial de Préstamos")
        theme = Settings.get_theme()
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {theme['TEXT_COLOR']};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Botón de registrar devolución
        self.return_btn = QPushButton("↩️ Registrar Devolución")
        self.return_btn.setStyleSheet(f"""
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
            QPushButton:disabled {{
                background-color: #BDBDBD;
            }}
        """)
        self.return_btn.setCursor(Qt.PointingHandCursor)
        self.return_btn.clicked.connect(self._register_return)
        self.return_btn.setEnabled(False)
        header_layout.addWidget(self.return_btn)
        
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
        self.search_input.setPlaceholderText("Buscar por ISBN o cédula...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                padding: 8px;
                font-size: 11pt;
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        self.search_input.textChanged.connect(self._filter_loans)
        filter_layout.addWidget(self.search_input, 1)
        
        layout.addWidget(filter_frame)
        
        # Tabla de préstamos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ISBN", "Número Ejemplar", "Cédula Solicitante", "Fecha Préstamo", "Fecha Devolución", "Fecha Devolución Máxima"
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
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
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
        
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
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
        
        self.total_label = QLabel("Total: 0 préstamos")
        self.total_label.setStyleSheet(f"color: {theme['TEXT_COLOR']};")
        stats_layout.addWidget(self.total_label)
        stats_layout.addStretch()
        
        self.pending_label = QLabel("Pendientes: 0")
        self.pending_label.setStyleSheet(f"color: {Settings.PRIMARY_COLOR};")
        stats_layout.addWidget(self.pending_label)
        
        self.returned_label = QLabel("Devueltos: 0")
        self.returned_label.setStyleSheet(f"color: {Settings.SUCCESS_COLOR};")
        stats_layout.addWidget(self.returned_label)
        
        layout.addWidget(stats_frame)
    
    def _load_sample_data(self):
        """Carga datos de ejemplo."""
        # Campos: ISBN, Número Ejemplar, Cédula Solicitante, Fecha Préstamo, Fecha Devolución, Fecha Devolución Máxima
        sample_loans = [
            ("978-0307474728", "1", "1102345678", "2026-01-10", "-", "2026-01-24"),
            ("978-0156012195", "2", "1103456789", "2026-01-05", "-", "2026-01-19"),
            ("978-0451524935", "1", "1104567890", "2026-01-15", "-", "2026-01-29"),
            ("978-0553380163", "1", "1105678901", "2025-12-20", "2026-01-02", "2026-01-03"),
            ("978-1599869773", "3", "1106789012", "2025-12-15", "2025-12-28", "2025-12-29"),
            ("978-0062316097", "1", "1107890123", "2026-01-12", "-", "2026-01-26"),
        ]
        
        self._populate_table(sample_loans)
    
    def _populate_table(self, loans):
        """Llena la tabla con los préstamos."""
        self.table.setRowCount(len(loans))
        
        for row, loan in enumerate(loans):
            for col, value in enumerate(loan):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Colorear fecha devolución (pendiente = rojo claro, devuelto = verde)
                if col == 4:  # Fecha Devolución
                    if value == "-":
                        item.setForeground(Qt.darkYellow)
                    else:
                        item.setForeground(Qt.darkGreen)
                
                self.table.setItem(row, col, item)
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        pending = 0
        returned = 0
        
        for row in range(total):
            item = self.table.item(row, 4)  # Columna Fecha Devolución
            if item:
                if item.text() == "-":
                    pending += 1
                else:
                    returned += 1
        
        self.total_label.setText(f"Total: {total} préstamos")
        self.pending_label.setText(f"Pendientes: {pending}")
        self.returned_label.setText(f"Devueltos: {returned}")
    
    def _filter_loans(self):
        """Filtra los préstamos según la búsqueda."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show = True
            
            if search_text:
                match = False
                for col in [0, 2]:  # ISBN, Cédula Solicitante
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                show = match
            
            self.table.setRowHidden(row, not show)
    
    def _on_selection_changed(self):
        """Maneja el cambio de selección."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            # Habilitar devolución si no tiene fecha de devolución
            return_date_item = self.table.item(row, 4)
            self.return_btn.setEnabled(
                return_date_item and return_date_item.text() == "-"
            )
        else:
            self.return_btn.setEnabled(False)
    
    def _register_return(self):
        """Registra la devolución de un préstamo."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            isbn = self.table.item(row, 0).text()
            cedula = self.table.item(row, 2).text()
            
            reply = QMessageBox.question(
                self,
                "Confirmar Devolución",
                f"¿Registrar devolución del préstamo?\n\nISBN: {isbn}\nCédula: {cedula}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Actualizar tabla - establecer fecha de devolución actual
                return_item = self.table.item(row, 4)
                return_item.setText("2026-01-19")
                return_item.setForeground(Qt.darkGreen)
                self._update_stats()
                self.return_btn.setEnabled(False)
                
                QMessageBox.information(
                    self,
                    "Devolución Registrada",
                    f"Se ha registrado la devolución del préstamo.\nISBN: {isbn}"
                )
