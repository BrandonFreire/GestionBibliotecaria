"""
Configuración general de la aplicación.
"""


class Settings:
    """Configuración general de la aplicación."""
    DARK_MODE = False  # Cambiar a True para modo oscuro
    
    # Colores - Modo Claro
    LIGHT_THEME = {
        "BG_COLOR": "#F5F5F5",
        "CARD_BG": "#FFFFFF",
        "TEXT_COLOR": "#333333",
        "TEXT_SECONDARY": "#757575",
        "SIDEBAR_BG": "#FFFFFF",
        "NAV_HOVER": "#E3F2FD",
        "BORDER_COLOR": "#E0E0E0",
        "USER_FRAME_BG": "#E3F2FD",
        "TABLE_ALT_ROW": "#FAFAFA",
        "INPUT_BG": "#FFFFFF",
        "LOGOUT_HOVER": "#FFEBEE",
    }
    
    # Colores - Modo Oscuro
    DARK_THEME = {
        "BG_COLOR": "#121212",
        "CARD_BG": "#1E1E1E",
        "TEXT_COLOR": "#E0E0E0",
        "TEXT_SECONDARY": "#9E9E9E",
        "SIDEBAR_BG": "#1E1E1E",
        "NAV_HOVER": "#2C2C2C",
        "BORDER_COLOR": "#333333",
        "USER_FRAME_BG": "#2C2C2C",
        "TABLE_ALT_ROW": "#252525",
        "INPUT_BG": "#2D2D2D",
        "LOGOUT_HOVER": "#3D2020",
    }
    
    # Información de la aplicación
    APP_NAME = "BD Distribuidas"
    APP_VERSION = "1.0.0"
    
    # Configuración de la ventana principal
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 500
    
    # Colores del tema (fijos)
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#1976D2"
    ERROR_COLOR = "#F44336"
    SUCCESS_COLOR = "#4CAF50"
    WARNING_COLOR = "#FF9800"
    
    # Fuentes
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 14
    FONT_SIZE_TITLE = 18
    
    @classmethod
    def get_theme(cls):
        """Retorna el tema actual."""
        return cls.DARK_THEME if cls.DARK_MODE else cls.LIGHT_THEME
    
    @classmethod
    def get(cls, key):
        """Obtiene un valor del tema actual."""
        return cls.get_theme().get(key, "")
    
    @classmethod
    def toggle_theme(cls):
        """Alterna entre modo claro y oscuro."""
        cls.DARK_MODE = not cls.DARK_MODE
        return cls.DARK_MODE
