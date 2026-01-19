"""
Funciones auxiliares.
"""
from datetime import datetime
from typing import Optional


def format_date(date: Optional[datetime], fmt: str = "%d/%m/%Y") -> str:
    """Formatea una fecha."""
    return date.strftime(fmt) if date else ""


def truncate_text(text: str, max_length: int = 50) -> str:
    """Trunca texto largo."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def safe_int(value, default: int = 0) -> int:
    """Convierte a int de forma segura."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
