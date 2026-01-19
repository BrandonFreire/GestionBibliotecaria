"""
Funciones de validación.
"""
import re
from typing import Any, Tuple


def validate_required(value: Any, field_name: str) -> Tuple[bool, str]:
    """Valida que un campo no esté vacío."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"El campo '{field_name}' es requerido"
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """Valida formato de email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, ""
    return False, "El formato del email no es válido"


def validate_length(value: str, min_len: int = 0, max_len: int = 255) -> Tuple[bool, str]:
    """Valida longitud de texto."""
    if len(value) < min_len:
        return False, f"Mínimo {min_len} caracteres"
    if len(value) > max_len:
        return False, f"Máximo {max_len} caracteres"
    return True, ""
