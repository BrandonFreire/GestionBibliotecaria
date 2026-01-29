"""
Vista de gestión de pasillos - PyQt5.
Conectada a la base de datos distribuida.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt

from config.settings import Settings
from database.distributed_connection import DistributedConnection
from database.s_p_pasillo import SP_Pasillo


class PasilloDialog(QDialog):
    """Diálogo para agregar/editar pasillo."""
    
    def __init__(self, parent=None, modo="agregar", pasillo_data=None, allowed_biblioteca=None):
        super().__init__(parent)
        self.modo = modo
        self.pasillo_data = pasillo_data or {}
        self.allowed_biblioteca = allowed_biblioteca
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle("Agregar Pasillo" if self.modo == "agregar" else "Editar Pasillo")
        self.setMinimumWidth(350)
        
        theme = Settings.get_theme()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['CARD_BG']};
            }}
            QLabel {{
                color: {theme['TEXT_COLOR']};
                font-size: 11pt;
            }}
            QComboBox, QSpinBox {{
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
        
        # Biblioteca
        self.biblioteca_combo = QComboBox()
        self.biblioteca_combo.addItems(["01 - FIS", "02 - FIQA"])
        if self.pasillo_data.get('id_biblioteca'):
            index = 0 if self.pasillo_data['id_biblioteca'] == '01' else 1
            self.biblioteca_combo.setCurrentIndex(index)
        
        # Si hay biblioteca fija (gestor), seleccionarla y deshabilitar
        if self.allowed_biblioteca:
            index = 0 if self.allowed_biblioteca == '01' else 1
            self.biblioteca_combo.setCurrentIndex(index)
            self.biblioteca_combo.setEnabled(False)
        elif self.modo == "editar":
            self.biblioteca_combo.setEnabled(False)
        form_layout.addRow("Biblioteca:", self.biblioteca_combo)
        
        # Número de pasillo
        self.num_pasillo_spin = QSpinBox()
        self.num_pasillo_spin.setMinimum(1)
        self.num_pasillo_spin.setMaximum(999)
        if self.pasillo_data.get('num_pasillo'):
            self.num_pasillo_spin.setValue(int(self.pasillo_data['num_pasillo']))
        if self.modo == "editar":
            self.num_pasillo_spin.setEnabled(False)
            # Para editar, necesitamos el nuevo número
            form_layout.addRow("Número Actual:", self.num_pasillo_spin)
            
            self.nuevo_num_spin = QSpinBox()
            self.nuevo_num_spin.setMinimum(1)
            self.nuevo_num_spin.setMaximum(999)
            self.nuevo_num_spin.setValue(int(self.pasillo_data.get('num_pasillo', 1)))
            form_layout.addRow("Nuevo Número:", self.nuevo_num_spin)
        else:
            form_layout.addRow("Número Pasillo:", self.num_pasillo_spin)
        
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
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def get_data(self):
        """Retorna los datos del formulario."""
        biblioteca_text = self.biblioteca_combo.currentText()
        id_biblioteca = '01' if '01' in biblioteca_text else '02'
        
        data = {
            'id_biblioteca': id_biblioteca,
            'num_pasillo': self.num_pasillo_spin.value()
        }
        
        if self.modo == "editar":
            data['num_pasillo_nuevo'] = self.nuevo_num_spin.value()
        
        return data


class PasilloView(QWidget):
    """Vista de gestión de pasillos."""
    
    def __init__(self, db_connection=None, current_user=None):
        """
        Inicializa la vista de pasillos.
        
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
        self.sp_pasillo = SP_Pasillo(self.dist_conn)
        
        self._create_widgets()
        self.load_data()  # Cargar datos reales de la BD
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🚪 Gestión de Pasillos")
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
        edit_btn.clicked.connect(self._edit_pasillo)
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
        delete_btn.clicked.connect(self._delete_pasillo)
        header_layout.addWidget(delete_btn)
        
        # Botón de nuevo pasillo
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
        new_btn.clicked.connect(self._add_pasillo)
        header_layout.addWidget(new_btn)
        
        layout.addLayout(header_layout)
        
        # Tabla de pasillos
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([
            "ID Biblioteca", "Número Pasillo"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
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
        
        self.total_label = QLabel("Total: 0 pasillos")
        self.total_label.setStyleSheet(f"color: {theme['TEXT_COLOR']};")
        stats_layout.addWidget(self.total_label)
        stats_layout.addStretch()
        
        layout.addWidget(stats_frame)
    
    def load_data(self):
        """Carga los datos de pasillos desde la base de datos distribuida."""
        try:
            # Consultar pasillos desde el nodo FIS
            pasillos = self.sp_pasillo.consultar_pasillo(node="FIS")
            
            # Filtrar por biblioteca permitida según rol
            if self.allowed_biblioteca and pasillos:
                pasillos = [p for p in pasillos if p.get('id_biblioteca') == self.allowed_biblioteca]
            
            if pasillos:
                self._populate_table(pasillos)
            else:
                self.table.setRowCount(0)
                self._update_stats()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar pasillos: {str(e)}"
            )
    
    def _populate_table(self, pasillos):
        """Llena la tabla con los pasillos desde la BD."""
        self.table.setSortingEnabled(False)
        
        self.table.setRowCount(len(pasillos))
        
        for row, pasillo in enumerate(pasillos):
            columns = [
                pasillo.get('id_biblioteca', ''),
                pasillo.get('num_pasillo', '')
            ]
            
            for col, value in enumerate(columns):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
        
        self.table.setSortingEnabled(True)
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        self.total_label.setText(f"Total: {total} pasillos")
    
    def _add_pasillo(self):
        """Abre el diálogo para agregar pasillo."""
        dialog = PasilloDialog(self, modo="agregar", allowed_biblioteca=self.allowed_biblioteca)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if data:
                try:
                    success = self.sp_pasillo.insertar_pasillo(
                        id_biblioteca=data['id_biblioteca'],
                        num_pasillo=data['num_pasillo'],
                        node='FIS'
                    )
                    
                    if success:
                        QMessageBox.information(
                            self,
                            "Éxito",
                            f"Pasillo {data['num_pasillo']} agregado correctamente."
                        )
                        self.load_data()
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "No se pudo agregar el pasillo. Verifique que no exista."
                        )
                        
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al agregar pasillo: {str(e)}"
                    )
    
    def _edit_pasillo(self):
        """Abre el diálogo para editar pasillo seleccionado."""
        current_row = self.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor seleccione un pasillo para editar."
            )
            return
        
        pasillo_data = {
            'id_biblioteca': self.table.item(current_row, 0).text(),
            'num_pasillo': self.table.item(current_row, 1).text()
        }
        
        dialog = PasilloDialog(self, modo="editar", pasillo_data=pasillo_data, allowed_biblioteca=self.allowed_biblioteca)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if data:
                try:
                    success = self.sp_pasillo.actualizar_pasillo(
                        id_biblioteca=data['id_biblioteca'],
                        num_pasillo_actual=data['num_pasillo'],
                        num_pasillo_nuevo=data['num_pasillo_nuevo'],
                        node='FIS'
                    )
                    
                    if success:
                        QMessageBox.information(
                            self,
                            "Éxito",
                            f"Pasillo actualizado correctamente."
                        )
                        self.load_data()
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "No se pudo actualizar el pasillo."
                        )
                        
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al actualizar pasillo: {str(e)}"
                    )
    
    def _delete_pasillo(self):
        """Elimina el pasillo seleccionado."""
        current_row = self.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor seleccione un pasillo para eliminar."
            )
            return
        
        id_biblioteca = self.table.item(current_row, 0).text()
        num_pasillo = int(self.table.item(current_row, 1).text())
        
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el pasillo {num_pasillo}?\n\n"
            f"Biblioteca: {id_biblioteca}\n\n"
            f"Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.sp_pasillo.eliminar_pasillo(
                    id_biblioteca=id_biblioteca,
                    num_pasillo=num_pasillo,
                    node='FIS'
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"Pasillo {num_pasillo} eliminado correctamente."
                    )
                    self.load_data()
                else:
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "No se pudo eliminar el pasillo. Puede tener libros asignados."
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al eliminar pasillo: {str(e)}"
                )
