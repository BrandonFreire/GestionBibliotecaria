"""
Vista de usuarios registrados - PyQt5.
Conectada a la base de datos distribuida.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt

from config.settings import Settings
from database.distributed_connection import DistributedConnection
from database.s_p_usuarios import SP_Usuarios
from gui.dialogs.usuario_dialog import UsuarioDialog


class UsuariosView(QWidget):
    """Vista de usuarios registrados."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa la vista de usuarios.
        
        Args:
            db_connection: Conexión legacy (ignorada, se usa DistributedConnection).
        """
        super().__init__()
        
        # Crear conexión distribuida propia
        self.dist_conn = DistributedConnection()
        self.sp_usuarios = SP_Usuarios(self.dist_conn)
        
        self._create_widgets()
        self.load_data()  # Cargar datos reales de la BD
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("👥 Usuarios Registrados")
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
        edit_btn.clicked.connect(self._edit_user)
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
        delete_btn.clicked.connect(self._delete_user)
        header_layout.addWidget(delete_btn)
        
        # Botón de nuevo usuario
        new_user_btn = QPushButton("➕ Nuevo")
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
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['CARD_BG']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        search_icon = QLabel("🔍")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar usuario por nombre o email...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                padding: 8px;
                font-size: 11pt;
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        self.search_input.textChanged.connect(self._filter_users)
        search_layout.addWidget(self.search_input, 1)
        
        layout.addWidget(search_frame)
        
        # Tabla de usuarios
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID Biblioteca", "Cédula", "Nombre", "Apellido", "Email", "Celular"
        ])
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
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
        
        self.table.doubleClicked.connect(self._show_user_details)
        
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
        
        self.total_label = QLabel("Total: 0 usuarios")
        self.total_label.setStyleSheet(f"color: {theme['TEXT_COLOR']};")
        stats_layout.addWidget(self.total_label)
        stats_layout.addStretch()
        
        layout.addWidget(stats_frame)
    
    def load_data(self):
        """Carga los datos de usuarios desde la base de datos."""
        try:
            # Consultar usuarios desde la base de datos
            usuarios = self.sp_usuarios.consultar_usuario(node="FIS")
            
            if usuarios:
                self._populate_table(usuarios)
            else:
                self.table.setRowCount(0)
                self._update_stats()
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar usuarios: {str(e)}"
            )
    
    def _populate_table(self, usuarios):
        """Llena la tabla con los usuarios desde la BD."""
        self.table.setRowCount(len(usuarios))
        
        for row, usuario in enumerate(usuarios):
            # Columnas: ID Biblioteca, Cédula, Nombre, Apellido, Email, Celular
            columns = [
                usuario.get('id_biblioteca', ''),
                usuario.get('cedula', ''),
                usuario.get('nombre_usuario', ''),
                usuario.get('apellido_usuario', ''),
                usuario.get('email_usuario', ''),
                usuario.get('celular_usuario', '')
            ]
            
            for col, value in enumerate(columns):
                item = QTableWidgetItem(str(value))
                # Centrar ID Biblioteca, Cédula y Celular
                if col in [0, 1, 5]:
                    item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(row, col, item)
        
        self._update_stats()
    
    def _update_stats(self):
        """Actualiza las estadísticas."""
        total = self.table.rowCount()
        self.total_label.setText(f"Total: {total} usuarios")
    
    def _filter_users(self):
        """Filtra los usuarios según la búsqueda."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            show = True
            
            if search_text:
                match = False
                # Buscar en: Cédula, Nombre, Apellido, Email
                for col in [1, 2, 3, 4]:
                    item = self.table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                show = match
            
            self.table.setRowHidden(row, not show)
    
    def _add_user(self):
        """Abre el diálogo para agregar usuario."""
        dialog = UsuarioDialog(self, modo="agregar")
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if data:
                try:
                    # Llamar al procedimiento almacenado
                    success = self.sp_usuarios.insertar_usuario(
                        id_biblioteca=data['id_biblioteca'],
                        cedula=data['cedula'],
                        nombre_usuario=data['nombre_usuario'],
                        apellido_usuario=data['apellido_usuario'],
                        email_usuario=data['email_usuario'],
                        celular_usuario=data['celular_usuario'],
                        node='FIS'
                    )
                    
                    if success:
                        QMessageBox.information(
                            self,
                            "Éxito",
                            f"Usuario {data['nombre_usuario']} {data['apellido_usuario']} agregado correctamente."
                        )
                        self.load_data()  # Recargar tabla
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "No se pudo agregar el usuario. Verifique que la cédula no exista."
                        )
                        
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al agregar usuario: {str(e)}"
                    )
    
    def _edit_user(self):
        """Abre el diálogo para editar usuario seleccionado."""
        # Verificar que hay una fila seleccionada
        current_row = self.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor seleccione un usuario para editar."
            )
            return
        
        # Obtener datos actuales de la fila
        usuario_data = {
            'id_biblioteca': self.table.item(current_row, 0).text(),
            'cedula': self.table.item(current_row, 1).text(),
            'nombre_usuario': self.table.item(current_row, 2).text(),
            'apellido_usuario': self.table.item(current_row, 3).text(),
            'email_usuario': self.table.item(current_row, 4).text(),
            'celular_usuario': self.table.item(current_row, 5).text()
        }
        
        # Abrir diálogo en modo editar
        dialog = UsuarioDialog(self, modo="editar", usuario_data=usuario_data)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if data:
                try:
                    # Llamar al procedimiento almacenado
                    success = self.sp_usuarios.actualizar_usuario(
                        id_biblioteca=data['id_biblioteca'],
                        cedula=data['cedula'],
                        nombre_usuario=data['nombre_usuario'],
                        apellido_usuario=data['apellido_usuario'],
                        email_usuario=data['email_usuario'],
                        celular_usuario=data['celular_usuario'],
                        node='FIS'
                    )
                    
                    if success:
                        QMessageBox.information(
                            self,
                            "Éxito",
                            f"Usuario {data['nombre_usuario']} {data['apellido_usuario']} actualizado correctamente."
                        )
                        self.load_data()  # Recargar tabla
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "No se pudo actualizar el usuario."
                        )
                        
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error al actualizar usuario: {str(e)}"
                    )
    
    def _delete_user(self):
        """Elimina el usuario seleccionado."""
        # Verificar que hay una fila seleccionada
        current_row = self.table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self,
                "Selección Requerida",
                "Por favor seleccione un usuario para eliminar."
            )
            return
        
        # Obtener datos del usuario
        id_biblioteca = self.table.item(current_row, 0).text()
        cedula = self.table.item(current_row, 1).text()
        nombre = self.table.item(current_row, 2).text()
        apellido = self.table.item(current_row, 3).text()
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar al usuario:\n\n"
            f"{nombre} {apellido}\n"
            f"Cédula: {cedula}\n\n"
            f"Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Llamar al procedimiento almacenado
                success = self.sp_usuarios.eliminar_usuario(
                    id_biblioteca=id_biblioteca,
                    cedula=cedula,
                    node='FIS'
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"Usuario {nombre} {apellido} eliminado correctamente."
                    )
                    self.load_data()  # Recargar tabla
                else:
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "No se pudo eliminar el usuario. Puede tener préstamos activos."
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al eliminar usuario: {str(e)}"
                )
    
    def _show_user_details(self, index):
        """Muestra los detalles del usuario."""
        row = index.row()
        user_info = f"""
        <b>ID Biblioteca:</b> {self.table.item(row, 0).text()}<br>
        <b>Cédula:</b> {self.table.item(row, 1).text()}<br>
        <b>Nombre:</b> {self.table.item(row, 2).text()}<br>
        <b>Apellido:</b> {self.table.item(row, 3).text()}<br>
        <b>Email:</b> {self.table.item(row, 4).text()}<br>
        <b>Celular:</b> {self.table.item(row, 5).text()}
        """
        
        QMessageBox.information(self, "Detalles del Usuario", user_info)
