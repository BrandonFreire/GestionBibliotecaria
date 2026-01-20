"""
Vista de login - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

from config.settings import Settings


class LoginView(QWidget):
    """Vista de inicio de sesión."""
    
    # Señal emitida cuando el login es exitoso
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_connection=None):
        super().__init__()
        self.db_connection = db_connection
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de la vista de login."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Panel izquierdo - Decorativo
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Settings.PRIMARY_COLOR},
                    stop:1 {Settings.SECONDARY_COLOR}
                );
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Icono de biblioteca
        icon_label = QLabel("📚")
        icon_label.setStyleSheet("font-size: 80px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(icon_label)
        
        welcome_label = QLabel("Sistema de Gestión\nBibliotecaria")
        welcome_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            background: transparent;
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(welcome_label)
        
        main_layout.addWidget(left_panel, 1)
        
        # Panel derecho - Formulario de login
        theme = Settings.get_theme()
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {theme['BG_COLOR']};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(60, 40, 60, 40)
        
        # Título
        title = QLabel("Iniciar Sesión")
        title.setStyleSheet(f"""
            font-size: {Settings.FONT_SIZE_TITLE}pt;
            font-weight: bold;
            color: {theme['TEXT_COLOR']};
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(title)
        
        # Formulario
        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['CARD_BG']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Campo de usuario
        user_label = QLabel("Usuario")
        user_label.setStyleSheet(f"color: {theme['TEXT_COLOR']}; font-weight: bold;")
        form_layout.addWidget(user_label)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingrese su usuario")
        self.user_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                font-size: 11pt;
                background-color: {theme['INPUT_BG']};
                color: {theme['TEXT_COLOR']};
            }}
            QLineEdit:focus {{
                border: 2px solid {Settings.PRIMARY_COLOR};
            }}
        """)
        form_layout.addWidget(self.user_input)
        
        # Campo de contraseña
        pass_label = QLabel("Contraseña")
        pass_label.setStyleSheet(f"color: {theme['TEXT_COLOR']}; font-weight: bold;")
        form_layout.addWidget(pass_label)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Ingrese su contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px;
                border: 1px solid {theme['BORDER_COLOR']};
                border-radius: 4px;
                font-size: 11pt;
                background-color: {theme['INPUT_BG']};
                color: {theme['TEXT_COLOR']};
            }}
            QLineEdit:focus {{
                border: 2px solid {Settings.PRIMARY_COLOR};
            }}
        """)
        self.pass_input.returnPressed.connect(self._login)
        form_layout.addWidget(self.pass_input)
        
        # Mensaje de error
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {Settings.ERROR_COLOR}; font-size: 10pt;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)
        
        # Botón de login
        login_btn = QPushButton("Iniciar Sesión")
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Settings.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Settings.SECONDARY_COLOR};
            }}
            QPushButton:pressed {{
                background-color: #1565C0;
            }}
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self._login)
        form_layout.addWidget(login_btn)
        
        right_layout.addWidget(form_frame)
        
        # Versión
        version_label = QLabel(f"v{Settings.APP_VERSION}")
        version_label.setStyleSheet(f"color: {theme['TEXT_SECONDARY']}; font-size: 9pt; margin-top: 20px;")
        version_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(version_label)
        
        main_layout.addWidget(right_panel, 1)
    
    def _login(self):
        """Procesa el intento de login."""
        username = self.user_input.text().strip()
        password = self.pass_input.text()
        
        if not username or not password:
            self._show_error("Por favor complete todos los campos")
            return
        
        # TODO: Validar contra base de datos
        # Por ahora, aceptamos cualquier credencial para demo
        if username and password:
            user_data = {
                'username': username,
                'name': username.title(),
                'role': 'admin' if username == 'admin' else 'user'
            }
            self.login_successful.emit(user_data)
        else:
            self._show_error("Usuario o contraseña incorrectos")
    
    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.error_label.setText(message)
        self.error_label.show()
    
    def clear(self):
        """Limpia los campos del formulario."""
        self.user_input.clear()
        self.pass_input.clear()
        self.error_label.hide()
