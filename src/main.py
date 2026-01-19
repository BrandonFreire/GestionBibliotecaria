"""
Punto de entrada principal de la aplicación.
"""
import sys
#from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    """Función principal que inicializa y ejecuta la aplicación."""
    # Cargar variables de entorno
    #load_dotenv()
    
    # Crear la aplicación Qt
    app = QApplication(sys.argv)
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar el loop principal
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
