"""
Componentes de formularios - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox,
    QPushButton, QSpinBox
)
from PyQt5.QtCore import Qt
from typing import Dict, Any, List, Callable, Optional

from config.settings import Settings


class FormBuilder(QWidget):
    """Constructor de formularios dinámicos."""
    
    def __init__(
        self,
        fields: List[Dict[str, Any]],
        on_submit: Optional[Callable[[Dict[str, Any]], None]] = None,
        parent=None
    ):
        """
        Inicializa el formulario.
        
        Args:
            fields: Lista de definiciones de campos.
                   Cada campo es un dict con: name, label, type, required, default
            on_submit: Callback al enviar el formulario.
            parent: Widget padre.
        """
        super().__init__(parent)
        
        self.fields = fields
        self.on_submit = on_submit
        self._widgets: Dict[str, QWidget] = {}
        
        self._create_form()
    
    def _create_form(self):
        """Crea el formulario basado en la definición de campos."""
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        for field in self.fields:
            name = field['name']
            label = field.get('label', name)
            field_type = field.get('type', 'text')
            required = field.get('required', False)
            default = field.get('default', '')
            
            # Label
            label_text = f"{label}{'*' if required else ''}:"
            label_widget = QLabel(label_text)
            
            # Widget según tipo
            if field_type == 'text':
                widget = QLineEdit()
                widget.setText(str(default))
            elif field_type == 'password':
                widget = QLineEdit()
                widget.setEchoMode(QLineEdit.Password)
                widget.setText(str(default))
            elif field_type == 'number':
                widget = QSpinBox()
                widget.setMaximum(999999999)
                widget.setValue(int(default) if default else 0)
            elif field_type == 'textarea':
                widget = QTextEdit()
                widget.setMaximumHeight(100)
                if default:
                    widget.setPlainText(str(default))
            elif field_type == 'checkbox':
                widget = QCheckBox()
                widget.setChecked(bool(default))
            elif field_type == 'select':
                widget = QComboBox()
                options = field.get('options', [])
                widget.addItems(options)
                if default in options:
                    widget.setCurrentText(default)
            else:
                widget = QLineEdit()
                widget.setText(str(default))
            
            widget.setMinimumWidth(300)
            form_layout.addRow(label_widget, widget)
            self._widgets[name] = widget
        
        layout.addLayout(form_layout)
        
        # Botón de enviar
        if self.on_submit:
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            
            submit_btn = QPushButton("Guardar")
            submit_btn.setStyleSheet(f"""
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
            submit_btn.setCursor(Qt.PointingHandCursor)
            submit_btn.clicked.connect(self._submit)
            btn_layout.addWidget(submit_btn)
            
            layout.addLayout(btn_layout)
    
    def get_values(self) -> Dict[str, Any]:
        """Obtiene los valores del formulario."""
        values = {}
        for field in self.fields:
            name = field['name']
            field_type = field.get('type', 'text')
            widget = self._widgets[name]
            
            if field_type == 'textarea':
                values[name] = widget.toPlainText().strip()
            elif field_type == 'checkbox':
                values[name] = widget.isChecked()
            elif field_type == 'number':
                values[name] = widget.value()
            elif field_type == 'select':
                values[name] = widget.currentText()
            else:
                values[name] = widget.text()
        
        return values
    
    def set_values(self, data: Dict[str, Any]):
        """Establece los valores del formulario."""
        for name, value in data.items():
            if name in self._widgets:
                field = next((f for f in self.fields if f['name'] == name), None)
                if field:
                    field_type = field.get('type', 'text')
                    widget = self._widgets[name]
                    
                    if field_type == 'textarea':
                        widget.setPlainText(str(value))
                    elif field_type == 'checkbox':
                        widget.setChecked(bool(value))
                    elif field_type == 'number':
                        widget.setValue(int(value))
                    elif field_type == 'select':
                        widget.setCurrentText(str(value))
                    else:
                        widget.setText(str(value))
    
    def clear(self):
        """Limpia el formulario."""
        for field in self.fields:
            name = field['name']
            field_type = field.get('type', 'text')
            default = field.get('default', '')
            widget = self._widgets[name]
            
            if field_type == 'textarea':
                widget.clear()
            elif field_type == 'checkbox':
                widget.setChecked(False)
            elif field_type == 'number':
                widget.setValue(int(default) if default else 0)
            elif field_type == 'select':
                widget.setCurrentIndex(0)
            else:
                widget.setText(str(default))
    
    def _submit(self):
        """Envía el formulario."""
        if self.on_submit:
            values = self.get_values()
            self.on_submit(values)
