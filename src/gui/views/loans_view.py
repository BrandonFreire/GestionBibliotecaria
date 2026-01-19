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


class LoansView(QWidget):
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
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {Settings.TEXT_COLOR};
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
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 5, 10, 5)
        
        # Búsqueda
        search_icon = QLabel("🔍")
        filter_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por usuario o libro...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 8px;
                font-size: 11pt;
            }
        """)
        self.search_input.textChanged.connect(self._filter_loans)
        filter_layout.addWidget(self.search_input, 1)
        
        # Filtro por estado
        filter_layout.addWidget(QLabel("Estado:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Activo", "Devuelto", "Vencido"])
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                min-width: 120px;
            }
        """)
        self.status_filter.currentTextChanged.connect(self._filter_loans)
        filter_layout.addWidget(self.status_filter)
        
        layout.addWidget(filter_frame)
        
        # Tabla de préstamos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Usuario", "Libro", "Fecha Préstamo", "Fecha Vencimiento", "Fecha Devolución", "Estado"
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
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
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
        
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
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
        
        self.total_label = QLabel("Total: 0 préstamos")
        stats_layout.addWidget(self.total_label)
        stats_layout.addStretch()
        
        self.active_label = QLabel("Activos: 0")
        self.active_label.setStyleSheet(f"color: {Settings.PRIMARY_COLOR};")
        stats_layout.addWidget(self.active_label)
        
        self.overdue_label = QLabel("Vencidos: 0")
        self.overdue_label.setStyleSheet(f"color: {Settings.ERROR_COLOR};")
        stats_layout.addWidget(self.overdue_label)
        
        layout.addWidget(stats_frame)
    
    def _load_sample_data(self):
        """Carga datos de ejemplo."""
        sample_loans = [
            (1, "Juan Pérez", "Cien años de soledad", "2026-01-10", "2026-01-24", "-", "Activo"),
            (2, "María García", "El principito", "2026-01-05", "2026-01-19", "-", "Vencido"),
            (3, "Carlos López", "1984", "2026-01-15", "2026-01-29", "-", "Activo"),
            (4, "Ana Martínez", "Breve historia del tiempo", "2025-12-20", "2026-01-03", "2026-01-02", "Devuelto"),
            (5, "Pedro Sánchez", "El arte de la guerra", "2025-12-15", "2025-12-29", "2025-12-28", "Devuelto"),
            (6, "Laura Torres", "Sapiens", "2026-01-12", "2026-01-26", "-", "Activo"),
        ]
        
        self._populate_table(sample_loans)
    
    def _populate_table(self, loans):
        """Llena la tabla con los préstamos."""
        self.table.setRowCount(len(loans))
        
        for row, loan in enumerate(loans):
            for col, value in enumerate(loan):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Colorear estado
                if col == 6:
                    if value == "Activo":
                        item.setForeground(Qt.darkGreen)
                    elif value == "Vencido":
                        item.setForeground(Qt.red)
                    else:
                        item.setForeground(Qt.gray)
                
                self.table.setItem(row, col, item)
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        active = 0
        overdue = 0
        
        for row in range(total):
            item = self.table.item(row, 6)
            if item:
                if item.text() == "Activo":
                    active += 1
                elif item.text() == "Vencido":
                    overdue += 1
        
        self.total_label.setText(f"Total: {total} préstamos")
        self.active_label.setText(f"Activos: {active}")
        self.overdue_label.setText(f"Vencidos: {overdue}")
    
    def _filter_loans(self):
        """Filtra los préstamos según la búsqueda."""
        search_text = self.search_input.text().lower()
        status = self.status_filter.currentText()
        
        for row in range(self.table.rowCount()):
            show = True
            
            if search_text:
                match = False
                for col in [1, 2]:  # Usuario, Libro
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                show = match
            
            if show and status != "Todos":
                status_item = self.table.item(row, 6)
                if status_item and status_item.text() != status:
                    show = False
            
            self.table.setRowHidden(row, not show)
    
    def _on_selection_changed(self):
        """Maneja el cambio de selección."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            status_item = self.table.item(row, 6)
            self.return_btn.setEnabled(
                status_item and status_item.text() in ["Activo", "Vencido"]
            )
        else:
            self.return_btn.setEnabled(False)
    
    def _register_return(self):
        """Registra la devolución de un préstamo."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            book = self.table.item(row, 2).text()
            user = self.table.item(row, 1).text()
            
            reply = QMessageBox.question(
                self,
                "Confirmar Devolución",
                f"¿Registrar devolución de:\n\n\"{book}\"\npor {user}?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Actualizar tabla
                self.table.item(row, 5).setText("2026-01-19")
                self.table.item(row, 6).setText("Devuelto")
                self.table.item(row, 6).setForeground(Qt.gray)
                self._update_stats()
                self.return_btn.setEnabled(False)
                
                QMessageBox.information(
                    self,
                    "Devolución Registrada",
                    f"Se ha registrado la devolución de:\n\"{book}\""
                )
