"""
Diálogos personalizados - PyQt5.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QWidget
)
from PyQt5.QtCore import Qt
from typing import Optional, Callable

from config.settings import Settings


class ConfirmDialog(QDialog):
    """Diálogo de confirmación personalizado."""
    
    def __init__(
        self,
        parent: QWidget,
        title: str,
        message: str,
        on_confirm: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None
    ):
        """
        Muestra un diálogo de confirmación.
        
        Args:
            parent: Widget padre.
            title: Título del diálogo.
            message: Mensaje a mostrar.
            on_confirm: Callback al confirmar.
            on_cancel: Callback al cancelar.
        """
        super().__init__(parent)
        
        self.result_value = False
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        
        self.setWindowTitle(title)
        self.setFixedSize(300, 150)
        self.setModal(True)
        
        self._create_widgets(message)
    
    def _create_widgets(self, message: str):
        """Crea los widgets del diálogo."""
        layout = QVBoxLayout(self)
        
        # Mensaje
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg_label)
        
        layout.addStretch()
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self._cancel)
        btn_layout.addWidget(cancel_btn)
        
        confirm_btn = QPushButton("Confirmar")
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Settings.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {Settings.SECONDARY_COLOR};
            }}
        """)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.clicked.connect(self._confirm)
        btn_layout.addWidget(confirm_btn)
        
        layout.addLayout(btn_layout)
    
    def _confirm(self):
        """Confirma el diálogo."""
        self.result_value = True
        if self.on_confirm:
            self.on_confirm()
        self.accept()
    
    def _cancel(self):
        """Cancela el diálogo."""
        self.result_value = False
        if self.on_cancel:
            self.on_cancel()
        self.reject()


class InputDialog(QDialog):
    """Diálogo de entrada de texto."""
    
    def __init__(
        self,
        parent: QWidget,
        title: str,
        prompt: str,
        default: str = ""
    ):
        """
        Muestra un diálogo de entrada.
        
        Args:
            parent: Widget padre.
            title: Título del diálogo.
            prompt: Texto del prompt.
            default: Valor por defecto.
        """
        super().__init__(parent)
        
        self.result_value: Optional[str] = None
        
        self.setWindowTitle(title)
        self.setFixedSize(350, 120)
        self.setModal(True)
        
        self._create_widgets(prompt, default)
    
    def _create_widgets(self, prompt: str, default: str):
        """Crea los widgets del diálogo."""
        layout = QVBoxLayout(self)
        
        # Prompt
        prompt_label = QLabel(prompt)
        layout.addWidget(prompt_label)
        
        # Input
        self.input_field = QLineEdit()
        self.input_field.setText(default)
        self.input_field.returnPressed.connect(self._accept)
        layout.addWidget(self.input_field)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self._cancel)
        btn_layout.addWidget(cancel_btn)
        
        accept_btn = QPushButton("Aceptar")
        accept_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Settings.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {Settings.SECONDARY_COLOR};
            }}
        """)
        accept_btn.setCursor(Qt.PointingHandCursor)
        accept_btn.clicked.connect(self._accept)
        btn_layout.addWidget(accept_btn)
        
        layout.addLayout(btn_layout)
    
    def _accept(self):
        """Acepta el diálogo."""
        self.result_value = self.input_field.text()
        self.accept()
    
    def _cancel(self):
        """Cancela el diálogo."""
        self.result_value = None
        self.reject()
