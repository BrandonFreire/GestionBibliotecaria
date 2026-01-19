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


class LibrosView(QWidget):
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
        self.category_filter.addItems(["Todas", "Computación", "Software", "Química"])
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ISBN", "Nombre", "Año de edición", "Categoría", "Lugar de impresión"
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
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
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
        # Estructura: (ISBN, Nombre, Año de edición, Categoría, Lugar de impresión)
        sample_books = [
            # Ciencias de la Computación
            ("978-0262033848", "Introduction to Algorithms", 2009, "Computación", "Cambridge, USA"),
            ("978-0201633610", "Design Patterns", 1994, "Software", "Boston, USA"),
            ("978-0132350884", "Clean Code", 2008, "Software", "New Jersey, USA"),
            ("978-0596007126", "Head First Design Patterns", 2004, "Software", "Sebastopol, USA"),
            ("978-0201485677", "The Pragmatic Programmer", 1999, "Software", "Boston, USA"),
            ("978-0596517748", "JavaScript: The Good Parts", 2008, "Software", "Sebastopol, USA"),
            ("978-1491950357", "Python Crash Course", 2015, "Computación", "San Francisco, USA"),
            ("978-0134685991", "Effective Java", 2017, "Software", "Boston, USA"),
            # Química
            ("978-6071509284", "Química General", 2014, "Química", "Ciudad de México, México"),
            ("978-0321910417", "Química Orgánica", 2017, "Química", "New York, USA"),
            ("978-8429175233", "Química Inorgánica", 2010, "Química", "Barcelona, España"),
            ("978-9702615149", "Fundamentos de Química", 2013, "Química", "Ciudad de México, México"),
            ("978-0073511092", "Química: La Ciencia Central", 2018, "Química", "New York, USA"),
            # Más Computación
            ("978-0596009205", "Learning Python", 2007, "Computación", "Sebastopol, USA"),
            ("978-1449355739", "Learning SQL", 2020, "Computación", "Sebastopol, USA"),
            ("978-0134757599", "Refactoring", 2018, "Software", "Boston, USA"),
        ]
        
        self._populate_table(sample_books)
    
    def _populate_table(self, books):
        """Llena la tabla con los libros."""
        self.table.setRowCount(len(books))
        
        for row, book in enumerate(books):
            for col, value in enumerate(book):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter if col in [0, 2] else Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        self.total_label.setText(f"Total: {total} libros")
        self.available_label.setText("")
    
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
        self.loan_btn.setEnabled(len(selected) > 0)
    
    def _request_loan(self):
        """Solicita un préstamo del libro seleccionado."""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            book_data = {
                'isbn': self.table.item(row, 0).text(),
                'title': self.table.item(row, 1).text(),
                'year': self.table.item(row, 2).text(),
                'category': self.table.item(row, 3).text(),
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
        <b>ISBN:</b> {self.table.item(row, 0).text()}<br>
        <b>Nombre:</b> {self.table.item(row, 1).text()}<br>
        <b>Año de edición:</b> {self.table.item(row, 2).text()}<br>
        <b>Categoría:</b> {self.table.item(row, 3).text()}<br>
        <b>Lugar de impresión:</b> {self.table.item(row, 4).text()}
        """
        
        QMessageBox.information(self, "Detalles del Libro", book_info)
