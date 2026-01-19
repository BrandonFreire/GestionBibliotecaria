"""
Vista del catálogo de libros - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from config.settings import Settings


class BooksView(QWidget):
    """Vista del catálogo de libros."""
    
    # Señal para solicitar préstamo
    loan_requested = pyqtSignal(dict)
    
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
        
        title = QLabel("📚 Catálogo de Libros")
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {Settings.TEXT_COLOR};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Botón de solicitar préstamo
        self.loan_btn = QPushButton("📖 Solicitar Préstamo")
        self.loan_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Settings.SUCCESS_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #43A047;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
            }}
        """)
        self.loan_btn.setCursor(Qt.PointingHandCursor)
        self.loan_btn.clicked.connect(self._request_loan)
        self.loan_btn.setEnabled(False)
        header_layout.addWidget(self.loan_btn)
        
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
        
        # Campo de búsqueda
        search_icon = QLabel("🔍")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por título, autor o ISBN...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 8px;
                font-size: 11pt;
            }
        """)
        self.search_input.textChanged.connect(self._filter_books)
        search_layout.addWidget(self.search_input, 1)
        
        # Filtro por categoría
        search_layout.addWidget(QLabel("Categoría:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["Todas", "Ficción", "No Ficción", "Ciencia", "Historia", "Arte"])
        self.category_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                min-width: 120px;
            }
        """)
        self.category_filter.currentTextChanged.connect(self._filter_books)
        search_layout.addWidget(self.category_filter)
        
        layout.addWidget(search_frame)
        
        # Tabla de libros
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Título", "Autor", "ISBN", "Categoría", "Disponibles"
        ])
        
        # Configurar tabla
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Configurar headers
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
        
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._show_book_details)
        
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
        
        self.total_label = QLabel("Total: 0 libros")
        stats_layout.addWidget(self.total_label)
        stats_layout.addStretch()
        self.available_label = QLabel("Disponibles: 0")
        self.available_label.setStyleSheet(f"color: {Settings.SUCCESS_COLOR};")
        stats_layout.addWidget(self.available_label)
        
        layout.addWidget(stats_frame)
    
    def _load_sample_data(self):
        """Carga datos de ejemplo."""
        sample_books = [
            (1, "Cien años de soledad", "Gabriel García Márquez", "978-0307474728", "Ficción", 3),
            (2, "El principito", "Antoine de Saint-Exupéry", "978-0156012195", "Ficción", 5),
            (3, "1984", "George Orwell", "978-0451524935", "Ficción", 2),
            (4, "Breve historia del tiempo", "Stephen Hawking", "978-0553380163", "Ciencia", 1),
            (5, "El arte de la guerra", "Sun Tzu", "978-1599869773", "Historia", 4),
            (6, "Sapiens", "Yuval Noah Harari", "978-0062316097", "Historia", 0),
            (7, "El código Da Vinci", "Dan Brown", "978-0307474278", "Ficción", 2),
            (8, "Cosmos", "Carl Sagan", "978-0345539434", "Ciencia", 3),
        ]
        
        self._populate_table(sample_books)
    
    def _populate_table(self, books):
        """Llena la tabla con los libros."""
        self.table.setRowCount(len(books))
        
        for row, book in enumerate(books):
            for col, value in enumerate(book):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter if col in [0, 5] else Qt.AlignLeft | Qt.AlignVCenter)
                
                # Colorear disponibilidad
                if col == 5:
                    if value == 0:
                        item.setForeground(Qt.red)
                        item.setText("No disponible")
                    else:
                        item.setForeground(Qt.darkGreen)
                
                self.table.setItem(row, col, item)
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        available = 0
        for row in range(total):
            item = self.table.item(row, 5)
            if item and item.text() != "No disponible":
                try:
                    available += int(item.text())
                except ValueError:
                    pass
        
        self.total_label.setText(f"Total: {total} libros")
        self.available_label.setText(f"Disponibles: {available} ejemplares")
    
    def _filter_books(self):
        """Filtra los libros según la búsqueda."""
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        
        for row in range(self.table.rowCount()):
            show = True
            
            # Filtrar por texto
            if search_text:
                match = False
                for col in [1, 2, 3]:  # Título, Autor, ISBN
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                show = match
            
            # Filtrar por categoría
            if show and category != "Todas":
                cat_item = self.table.item(row, 4)
                if cat_item and cat_item.text() != category:
                    show = False
            
            self.table.setRowHidden(row, not show)
    
    def _on_selection_changed(self):
        """Maneja el cambio de selección."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            available_item = self.table.item(row, 5)
            self.loan_btn.setEnabled(
                available_item and available_item.text() != "No disponible"
            )
        else:
            self.loan_btn.setEnabled(False)
    
    def _request_loan(self):
        """Solicita un préstamo del libro seleccionado."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            book_data = {
                'id': self.table.item(row, 0).text(),
                'title': self.table.item(row, 1).text(),
                'author': self.table.item(row, 2).text(),
            }
            
            reply = QMessageBox.question(
                self,
                "Confirmar Préstamo",
                f"¿Desea solicitar el préstamo de:\n\n\"{book_data['title']}\"?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.loan_requested.emit(book_data)
                QMessageBox.information(
                    self,
                    "Préstamo Registrado",
                    f"Se ha registrado el préstamo de:\n\"{book_data['title']}\""
                )
    
    def _show_book_details(self, index):
        """Muestra los detalles del libro."""
        row = index.row()
        book_info = f"""
        <b>Título:</b> {self.table.item(row, 1).text()}<br>
        <b>Autor:</b> {self.table.item(row, 2).text()}<br>
        <b>ISBN:</b> {self.table.item(row, 3).text()}<br>
        <b>Categoría:</b> {self.table.item(row, 4).text()}<br>
        <b>Disponibles:</b> {self.table.item(row, 5).text()}
        """
        
        QMessageBox.information(self, "Detalles del Libro", book_info)
