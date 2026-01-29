"""
Vista del catálogo de libros - PyQt5.
Conectada a la base de datos distribuida.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QMessageBox,
    QDialog, QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from config.settings import Settings
from database.distributed_connection import DistributedConnection
from database.s_p_libro import SP_Libro


class LibrosView(QWidget):
    """Vista del catálogo de libros."""
    
    # Señal para solicitar préstamo
    loan_requested = pyqtSignal(dict)
    
    def __init__(self, db_connection=None):
        """
        Inicializa la vista de libros.
        
        Args:
            db_connection: Conexión legacy (ignorada, se usa DistributedConnection).
        """
        super().__init__()
        
        # Crear conexión distribuida propia
        self.dist_conn = DistributedConnection()
        self.sp_libro = SP_Libro(self.dist_conn)
        
        self._create_widgets()
        self.load_data()  # Cargar datos reales de la BD
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📚 Catálogo de Libros")
        theme = Settings.get_theme()
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {theme['TEXT_COLOR']};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Botón de refrescar
        refresh_btn = QPushButton("🔄 Refrescar")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Settings.SECONDARY_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {Settings.PRIMARY_COLOR};
            }}
        """)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        # Botón de editar
        edit_btn = QPushButton("✏️ Editar")
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFA500;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #FF8C00;
            }}
        """)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self._edit_libro)
        header_layout.addWidget(edit_btn)
        
        # Botón de eliminar
        delete_btn = QPushButton("🗑️ Eliminar")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #C82333;
            }}
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self._delete_libro)
        header_layout.addWidget(delete_btn)
        
        # Botón de nuevo libro
        new_btn = QPushButton("➕ Nuevo")
        new_btn.setStyleSheet(f"""
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
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.clicked.connect(self._add_libro)
        header_layout.addWidget(new_btn)
        
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
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['CARD_BG']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        # Campo de búsqueda
        search_icon = QLabel("🔍")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por título, autor o ISBN...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                padding: 8px;
                font-size: 11pt;
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        self.search_input.textChanged.connect(self._filter_books)
        search_layout.addWidget(self.search_input, 1)
        
        # Filtro por categoría
        cat_label = QLabel("Categoría:")
        cat_label.setStyleSheet(f"color: {theme['TEXT_COLOR']};")
        search_layout.addWidget(cat_label)
        self.category_filter = QComboBox()
        self.category_filter.addItems(["Todas", "Computación", "Software", "Química"])
        self.category_filter.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                min-width: 120px;
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
            }}
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
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme['CARD_BG']};
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 8px;
                gridline-color: {theme['BORDER_COLOR']};
                color: {theme['TEXT_COLOR']};
                alternate-background-color: {theme['TABLE_ALT_ROW']};
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {theme['TEXT_COLOR']};
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
        self.table.doubleClicked.connect(self._show_book_details)
        
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
        
        self.total_label = QLabel("Total: 0 libros")
        self.total_label.setStyleSheet(f"color: {theme['TEXT_COLOR']};")
        stats_layout.addWidget(self.total_label)
        stats_layout.addStretch()
        self.available_label = QLabel("Disponibles: 0")
        self.available_label.setStyleSheet(f"color: {Settings.SUCCESS_COLOR};")
        stats_layout.addWidget(self.available_label)
        
        layout.addWidget(stats_frame)
    
    def load_data(self):
        """Carga los datos de libros desde la base de datos distribuida."""
        try:
            # Consultar libros desde el nodo FIS (publicador en replicación)
            libros = self.sp_libro.consultar_libro(node="FIS")
            
            if libros:
                self._populate_table(libros)
            else:
                self.table.setRowCount(0)
                self._update_stats()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar libros: {str(e)}"
            )
    
    def _populate_table(self, libros):
        """Llena la tabla con los libros desde la BD."""
        self.table.setSortingEnabled(False)
        
        self.table.setRowCount(len(libros))
        
        for row, libro in enumerate(libros):
            # Columnas: ISBN, Nombre, Año de edición, Categoría, Lugar de impresión
            columns = [
                libro.get('ISBN', ''),
                libro.get('nombre_libro', ''),
                libro.get('anio_edicion', ''),
                libro.get('categoria_libro', ''),
                libro.get('lugar_impresion_libro', '')
            ]
            
            for col, value in enumerate(columns):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter if col in [0, 2] else Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)
        
        self.table.setSortingEnabled(True)
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
    
    def _add_libro(self):
        """Abre el diálogo para agregar un nuevo libro."""
        dialog = LibroDialog(self, modo="agregar")
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if data:
                try:
                    success = self.sp_libro.insertar_libro(
                        ISBN=data['ISBN'],
                        nombre_libro=data['nombre_libro'],
                        anio_edicion=data['anio_edicion'],
                        categoria_libro=data['categoria_libro'],
                        lugar_impresion_libro=data['lugar_impresion_libro'],
                        node='FIS'
                    )
                    
                    if success:
                        QMessageBox.information(
                            self,
                            "Éxito",
                            f"Libro '{data['nombre_libro']}' agregado correctamente."
                        )
                        self.load_data()
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "No se pudo agregar el libro. Verifique que el ISBN no exista."
                        )
                        
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al agregar libro: {str(e)}"
                    )
    
    def _edit_libro(self):
        """Abre el diálogo para editar el libro seleccionado."""
        current_row = self.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor seleccione un libro para editar."
            )
            return
        
        libro_data = {
            'ISBN': self.table.item(current_row, 0).text(),
            'nombre_libro': self.table.item(current_row, 1).text(),
            'anio_edicion': self.table.item(current_row, 2).text(),
            'categoria_libro': self.table.item(current_row, 3).text(),
            'lugar_impresion_libro': self.table.item(current_row, 4).text()
        }
        
        dialog = LibroDialog(self, modo="editar", libro_data=libro_data)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if data:
                try:
                    success = self.sp_libro.actualizar_libro(
                        ISBN=data['ISBN'],
                        nombre_libro=data['nombre_libro'],
                        anio_edicion=data['anio_edicion'],
                        categoria_libro=data['categoria_libro'],
                        lugar_impresion_libro=data['lugar_impresion_libro'],
                        node='FIS'
                    )
                    
                    if success:
                        QMessageBox.information(
                            self,
                            "Éxito",
                            f"Libro actualizado correctamente."
                        )
                        self.load_data()
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "No se pudo actualizar el libro."
                        )
                        
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al actualizar libro: {str(e)}"
                    )
    
    def _delete_libro(self):
        """Elimina el libro seleccionado."""
        current_row = self.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor seleccione un libro para eliminar."
            )
            return
        
        isbn = self.table.item(current_row, 0).text()
        nombre = self.table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el libro?\n\n"
            f"ISBN: {isbn}\n"
            f"Nombre: {nombre}\n\n"
            f"Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.sp_libro.eliminar_libro(
                    ISBN=isbn,
                    node='FIS'
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"Libro '{nombre}' eliminado correctamente."
                    )
                    self.load_data()
                else:
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "No se pudo eliminar el libro. Puede tener ejemplares o préstamos asociados."
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al eliminar libro: {str(e)}"
                )


class LibroDialog(QDialog):
    """Diálogo para agregar/editar libro."""
    
    def __init__(self, parent=None, modo="agregar", libro_data=None):
        super().__init__(parent)
        self.modo = modo
        self.libro_data = libro_data or {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle("Agregar Libro" if self.modo == "agregar" else "Editar Libro")
        self.setMinimumWidth(450)
        
        theme = Settings.get_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['CARD_BG']};
            }}
            QLabel {{
                color: {theme['TEXT_COLOR']};
                font-size: 11pt;
            }}
            QLineEdit, QSpinBox {{
                padding: 8px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
                font-size: 11pt;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # ISBN
        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText("Ej: 978-0132350884")
        if self.libro_data.get('ISBN'):
            self.isbn_input.setText(self.libro_data['ISBN'])
        if self.modo == "editar":
            self.isbn_input.setEnabled(False)
        form_layout.addRow("ISBN:", self.isbn_input)
        
        # Nombre del libro
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del libro")
        if self.libro_data.get('nombre_libro'):
            self.nombre_input.setText(self.libro_data['nombre_libro'])
        form_layout.addRow("Nombre:", self.nombre_input)
        
        # Año de edición
        self.anio_spin = QSpinBox()
        self.anio_spin.setMinimum(1900)
        self.anio_spin.setMaximum(2100)
        self.anio_spin.setValue(2024)
        if self.libro_data.get('anio_edicion'):
            self.anio_spin.setValue(int(self.libro_data['anio_edicion']))
        form_layout.addRow("Año de Edición:", self.anio_spin)
        
        # Categoría
        self.categoria_input = QLineEdit()
        self.categoria_input.setPlaceholderText("Ej: Computación, Software, Química")
        if self.libro_data.get('categoria_libro'):
            self.categoria_input.setText(self.libro_data['categoria_libro'])
        form_layout.addRow("Categoría:", self.categoria_input)
        
        # Lugar de impresión
        self.lugar_input = QLineEdit()
        self.lugar_input.setPlaceholderText("Ej: New York, USA")
        if self.libro_data.get('lugar_impresion_libro'):
            self.lugar_input.setText(self.libro_data['lugar_impresion_libro'])
        form_layout.addRow("Lugar de Impresión:", self.lugar_input)
        
        layout.addLayout(form_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 4px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #5a6268;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Settings.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 4px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {Settings.SECONDARY_COLOR};
            }}
        """)
        save_btn.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _validate_and_accept(self):
        """Valida los datos antes de aceptar."""
        if not self.isbn_input.text().strip():
            QMessageBox.warning(self, "Validación", "El ISBN es requerido.")
            return
        if not self.nombre_input.text().strip():
            QMessageBox.warning(self, "Validación", "El nombre del libro es requerido.")
            return
        self.accept()
    
    def get_data(self):
        """Retorna los datos del formulario."""
        return {
            'ISBN': self.isbn_input.text().strip(),
            'nombre_libro': self.nombre_input.text().strip(),
            'anio_edicion': self.anio_spin.value(),
            'categoria_libro': self.categoria_input.text().strip(),
            'lugar_impresion_libro': self.lugar_input.text().strip()
        }

