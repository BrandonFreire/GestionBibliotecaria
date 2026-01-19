"""
Componente de tabla de datos - PyQt5.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any, Optional


class DataTable(QWidget):
    """Tabla de datos con scrolling y selección."""
    
    # Señal emitida cuando se selecciona una fila
    row_selected = pyqtSignal(dict)
    
    def __init__(
        self,
        columns: List[str],
        data: Optional[List[Dict[str, Any]]] = None,
        parent=None
    ):
        """
        Inicializa la tabla de datos.
        
        Args:
            columns: Lista de nombres de columnas.
            data: Datos iniciales para mostrar.
            parent: Widget padre.
        """
        super().__init__(parent)
        
        self.columns = columns
        self._data: List[Dict[str, Any]] = []
        
        self._create_widgets()
        
        if data:
            self.load_data(data)
    
    def _create_widgets(self):
        """Crea los widgets de la tabla."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear tabla
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        
        # Configurar comportamiento
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        # Configurar headers
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # Estilo
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        # Conectar señal de selección
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.table)
    
    def load_data(self, data: List[Dict[str, Any]]):
        """
        Carga datos en la tabla.
        
        Args:
            data: Lista de diccionarios con los datos.
        """
        self.clear()
        self._data = data
        
        self.table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, col_name in enumerate(self.columns):
                value = row_data.get(col_name, '')
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
    
    def clear(self):
        """Limpia todos los datos de la tabla."""
        self._data = []
        self.table.setRowCount(0)
    
    def get_selected(self) -> Optional[Dict[str, Any]]:
        """Obtiene la fila seleccionada."""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row_idx = selected_rows[0].row()
            return self._data[row_idx] if row_idx < len(self._data) else None
        return None
    
    def _on_selection_changed(self):
        """Maneja el evento de selección."""
        selected = self.get_selected()
        if selected:
            self.row_selected.emit(selected)
