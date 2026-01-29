"""
Diálogo para agregar/editar usuarios.
"""
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from config.settings import Settings


class UsuarioDialog(QDialog):
    """Diálogo para agregar o editar un usuario."""
    
    def __init__(self, parent=None, modo="agregar", usuario_data=None, allowed_biblioteca=None):
        """
        Inicializa el diálogo.
        
        Args:
            parent: Widget padre.
            modo: "agregar" o "editar".
            usuario_data: Diccionario con datos del usuario (solo para modo editar).
            allowed_biblioteca: Biblioteca fija para gestores ('01' o '02'). None para admin.
        """
        super().__init__(parent)
        self.modo = modo
        self.usuario_data = usuario_data or {}
        self.allowed_biblioteca = allowed_biblioteca
        self.result_data = None
        
        self.setWindowTitle("Nuevo Usuario" if modo == "agregar" else "Editar Usuario")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        theme = Settings.get_theme()
        
        # Título
        title = QLabel("Nuevo Usuario" if self.modo == "agregar" else "Editar Usuario")
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {theme['TEXT_COLOR']};
            padding-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Formulario
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['CARD_BG']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(12)
        
        # ID Biblioteca
        self.biblioteca_combo = QComboBox()
        self.biblioteca_combo.addItems(["01 - FIS", "02 - FIQA"])
        self.biblioteca_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                background-color: {theme['BG_COLOR']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        
        # Si hay biblioteca fija (gestor), seleccionarla y deshabilitar el combo
        if self.allowed_biblioteca:
            index = 0 if self.allowed_biblioteca == '01' else 1
            self.biblioteca_combo.setCurrentIndex(index)
            self.biblioteca_combo.setEnabled(False)
        
        form_layout.addRow("Biblioteca:", self.biblioteca_combo)
        
        # Cédula
        self.cedula_input = QLineEdit()
        self.cedula_input.setPlaceholderText("Ej: 1700000001")
        self.cedula_input.setMaxLength(10)
        if self.modo == "editar":
            self.cedula_input.setReadOnly(True)  # No editable en modo editar
            self.cedula_input.setStyleSheet(f"""
                QLineEdit {{
                    padding: 8px;
                    border: 1px solid {theme['BORDER_COLOR']};
                    border-radius: 4px;
                    background-color: {theme['TABLE_ALT_ROW']};
                    color: {theme['TEXT_COLOR']};
                }}
            """)
        else:
            self.cedula_input.setStyleSheet(f"""
                QLineEdit {{
                    padding: 8px;
                    border: 1px solid {theme['BORDER_COLOR']};
                    border-radius: 4px;
                    background-color: {theme['BG_COLOR']};
                    color: {theme['TEXT_COLOR']};
                }}
            """)
        form_layout.addRow("Cédula*:", self.cedula_input)
        
        # Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Juan")
        self.nombre_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                background-color: {theme['BG_COLOR']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        form_layout.addRow("Nombre*:", self.nombre_input)
        
        # Apellido
        self.apellido_input = QLineEdit()
        self.apellido_input.setPlaceholderText("Ej: Pérez")
        self.apellido_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                background-color: {theme['BG_COLOR']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        form_layout.addRow("Apellido*:", self.apellido_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ej: juan.perez@example.com")
        self.email_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                background-color: {theme['BG_COLOR']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        form_layout.addRow("Email*:", self.email_input)
        
        # Celular
        self.celular_input = QLineEdit()
        self.celular_input.setPlaceholderText("Ej: 0987654321")
        self.celular_input.setMaxLength(10)
        self.celular_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                background-color: {theme['BG_COLOR']};
                color: {theme['TEXT_COLOR']};
            }}
        """)
        form_layout.addRow("Celular*:", self.celular_input)
        
        layout.addWidget(form_frame)
        
        # Nota de campos requeridos
        note = QLabel("* Campos requeridos")
        note.setStyleSheet(f"color: {theme['TEXT_COLOR']}; font-size: 9pt; font-style: italic;")
        layout.addWidget(note)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['BORDER_COLOR']};
                color: {theme['TEXT_COLOR']};
                border: none;
                padding: 10px 25px;
                border-radius: 4px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {theme['USER_FRAME_BG']};
            }}
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
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
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_data(self):
        """Carga los datos del usuario en modo editar."""
        if self.modo == "editar" and self.usuario_data:
            # Seleccionar biblioteca
            id_bib = self.usuario_data.get('id_biblioteca', '01')
            index = 0 if id_bib == '01' else 1
            self.biblioteca_combo.setCurrentIndex(index)
            
            # Cargar campos
            self.cedula_input.setText(self.usuario_data.get('cedula', ''))
            self.nombre_input.setText(self.usuario_data.get('nombre_usuario', ''))
            self.apellido_input.setText(self.usuario_data.get('apellido_usuario', ''))
            self.email_input.setText(self.usuario_data.get('email_usuario', ''))
            self.celular_input.setText(self.usuario_data.get('celular_usuario', ''))
    
    def _validar_cedula(self, cedula: str) -> bool:
        """Valida que la cédula sea correcta."""
        return cedula.isdigit() and len(cedula) == 10
    
    def _validar_email(self, email: str) -> bool:
        """Valida que el email tenga formato correcto."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    def _validar_celular(self, celular: str) -> bool:
        """Valida que el celular sea correcto."""
        return celular.isdigit() and len(celular) == 10 and celular.startswith('09')
    
    def _save(self):
        """Valida y guarda los datos."""
        # Obtener valores
        id_biblioteca = '01' if self.biblioteca_combo.currentIndex() == 0 else '02'
        cedula = self.cedula_input.text().strip()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        email = self.email_input.text().strip()
        celular = self.celular_input.text().strip()
        
        # Validar campos vacíos
        if not all([cedula, nombre, apellido, email, celular]):
            QMessageBox.warning(
                self,
                "Campos Incompletos",
                "Por favor complete todos los campos requeridos."
            )
            return
        
        # Validar cédula
        if not self._validar_cedula(cedula):
            QMessageBox.warning(
                self,
                "Cédula Inválida",
                "La cédula debe tener 10 dígitos numéricos."
            )
            self.cedula_input.setFocus()
            return
        
        # Validar email
        if not self._validar_email(email):
            QMessageBox.warning(
                self,
                "Email Inválido",
                "Por favor ingrese un email válido."
            )
            self.email_input.setFocus()
            return
        
        # Validar celular
        if not self._validar_celular(celular):
            QMessageBox.warning(
                self,
                "Celular Inválido",
                "El celular debe tener 10 dígitos y comenzar con 09."
            )
            self.celular_input.setFocus()
            return
        
        # Guardar datos
        self.result_data = {
            'id_biblioteca': id_biblioteca,
            'cedula': cedula,
            'nombre_usuario': nombre,
            'apellido_usuario': apellido,
            'email_usuario': email,
            'celular_usuario': celular
        }
        
        self.accept()
    
    def get_data(self):
        """Retorna los datos ingresados."""
        return self.result_data
