"""
Vista de historial de préstamos - PyQt5.
Conectada a la base de datos distribuida.
"""
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt

from config.settings import Settings
from database.distributed_connection import DistributedConnection
from database.s_p_prestamo import SP_Prestamo


class PrestamosView(QWidget):
    """Vista de historial de préstamos."""
    
    def __init__(self, db_connection=None, current_user=None):
        """
        Inicializa la vista de préstamos.
        
        Args:
            db_connection: Conexión legacy (ignorada, se usa DistributedConnection).
            current_user: Datos del usuario autenticado para control de acceso.
        """
        super().__init__()
        
        # Guardar información del usuario actual
        self.current_user = current_user or {}
        self.user_role = self.current_user.get('role', 'usuario')
        
        # Determinar biblioteca permitida según rol
        if self.user_role == 'admin':
            self.allowed_biblioteca = None  # Todas las bibliotecas
        elif self.user_role == 'gestor_fis':
            self.allowed_biblioteca = '01'  # Solo FIS
        elif self.user_role == 'gestor_fiqa':
            self.allowed_biblioteca = '02'  # Solo FIQA
        else:
            self.allowed_biblioteca = None  # Solo lectura
        
        # Crear conexión distribuida propia
        self.dist_conn = DistributedConnection()
        self.sp_prestamo = SP_Prestamo(self.dist_conn)
        
        self._create_widgets()
        self.load_data()  # Cargar datos reales de la BD
    
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID Biblioteca", "ISBN", "ID Ejemplar", "Cédula", "Fecha Préstamo", "Fecha Devolución", "Fecha Dev. Máx."
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
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
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
    
    def load_data(self):
        """Carga los datos de préstamos desde la base de datos distribuida."""
        try:
            # Consultar préstamos desde el nodo FIS (los SP con vistas están en FIS)
            prestamos = self.sp_prestamo.consultar_prestamo(node="FIS")
            
            # Filtrar por biblioteca permitida según rol
            if self.allowed_biblioteca and prestamos:
                prestamos = [p for p in prestamos if p.get('id_biblioteca') == self.allowed_biblioteca]
            
            if prestamos:
                self._populate_table(prestamos)
            else:
                self.table.setRowCount(0)
                self._update_stats()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar préstamos: {str(e)}"
            )
    
    def _populate_table(self, prestamos):
        """Llena la tabla con los préstamos desde la BD."""
        # Deshabilitar sorting temporalmente para evitar problemas
        self.table.setSortingEnabled(False)
        
        self.table.setRowCount(len(prestamos))
        
        for row, prestamo in enumerate(prestamos):
            # Columnas: ID Biblioteca, ISBN, ID Ejemplar, Cédula, Fecha Préstamo, Fecha Devolución, Fecha Dev. Máx.
            fecha_devolucion = prestamo.get('fecha_devolucion', None)
            fecha_devolucion_str = str(fecha_devolucion) if fecha_devolucion else "-"
            
            columns = [
                prestamo.get('id_biblioteca', ''),
                prestamo.get('ISBN', ''),
                prestamo.get('id_ejemplar', ''),
                prestamo.get('cedula', ''),
                str(prestamo.get('fecha_prestamo', '')),
                fecha_devolucion_str,
                str(prestamo.get('fecha_devolucion_tope', ''))
            ]
            
            for col, value in enumerate(columns):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                
                # Colorear fecha devolución (pendiente = amarillo, devuelto = verde)
                if col == 5:  # Fecha Devolución
                    if value == "-" or value == "None":
                        item.setForeground(Qt.darkYellow)
                        item.setText("-")
                    else:
                        item.setForeground(Qt.darkGreen)
                
                self.table.setItem(row, col, item)
        
        # Rehabilitar sorting
        self.table.setSortingEnabled(True)
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        pending = 0
        returned = 0
        
        for row in range(total):
            item = self.table.item(row, 5)  # Columna Fecha Devolución (índice 5)
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
                for col in [1, 3]:  # ISBN (índice 1), Cédula (índice 3)
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
            return_date_item = self.table.item(row, 5)  # Fecha Devolución (índice 5)
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
            
            # Obtener datos de la fila seleccionada
            id_biblioteca = self.table.item(row, 0).text()
            isbn = self.table.item(row, 1).text()
            id_ejemplar = int(self.table.item(row, 2).text())
            cedula = self.table.item(row, 3).text()
            fecha_prestamo_str = self.table.item(row, 4).text()
            
            reply = QMessageBox.question(
                self,
                "Confirmar Devolución",
                f"¿Registrar devolución del préstamo?\n\n"
                f"ISBN: {isbn}\n"
                f"Cédula: {cedula}\n"
                f"Fecha Préstamo: {fecha_prestamo_str}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    # Convertir fecha_prestamo string a date
                    from datetime import datetime
                    fecha_prestamo = datetime.strptime(fecha_prestamo_str.split()[0], '%Y-%m-%d').date()
                    fecha_devolucion = date.today()
                    
                    # Determinar el nodo según el id_biblioteca
                    node = 'FIS' if id_biblioteca == '01' else 'FIQA'
                    
                    # Llamar al procedimiento almacenado en el nodo correspondiente
                    success = self.sp_prestamo.actualizar_prestamo(
                        id_biblioteca=id_biblioteca,
                        ISBN=isbn,
                        id_ejemplar=id_ejemplar,
                        cedula=cedula,
                        fecha_prestamo=fecha_prestamo,
                        fecha_devolucion_nueva=fecha_devolucion,
                        node=node
                    )
                    
                    if success:
                        QMessageBox.information(
                            self,
                            "Devolución Registrada",
                            f"Se ha registrado la devolución del préstamo.\nISBN: {isbn}"
                        )
                        self.load_data()  # Recargar tabla
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "No se pudo registrar la devolución."
                        )
                        
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al registrar devolución: {str(e)}"
                    )
