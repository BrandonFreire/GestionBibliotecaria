"""
Modelos de datos para la aplicación.
Aquí puedes definir clases que representen las entidades de tu base de datos.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


# Ejemplo de modelo - Modifica según tus necesidades
@dataclass
class ExampleModel:
    """
    Modelo de ejemplo.
    Reemplaza o modifica según las tablas de tu base de datos.
    """
    id: Optional[int] = None
    nombre: str = ""
    descripcion: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    activo: bool = True
    
    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion,
            'activo': self.activo
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ExampleModel":
        """Crea una instancia desde un diccionario."""
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion'),
            fecha_creacion=data.get('fecha_creacion'),
            activo=data.get('activo', True)
        )


# Agrega más modelos según tus tablas
# @dataclass
# class OtroModelo:
#     ...
