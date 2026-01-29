"""
Ventana principal de la aplicación - Sistema de Gestión Bibliotecaria.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget,
    QMenuBar, QMenu, QAction, QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from config.settings import Settings
from database.connection import DatabaseConnection
from gui.views.login_view import LoginView
from gui.views.libros_view import LibrosView
from gui.views.usuarios_view import UsuariosView
from gui.views.prestamos_view import PrestamosView
from gui.views.ejemplares_view import EjemplaresView
from gui.views.pasillo_view import PasilloView


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()
        self.db_connection = DatabaseConnection()
        self.current_user = None
        
        self._setup_window()
        self._create_stacked_widget()
        self._show_login()
    
    def _setup_window(self):
        """Configura las propiedades de la ventana."""
        self.setWindowTitle(f"{Settings.APP_NAME} v{Settings.APP_VERSION}")
        self.setMinimumSize(Settings.WINDOW_MIN_WIDTH, Settings.WINDOW_MIN_HEIGHT)
        self.resize(Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT)
        
        # Centrar la ventana
        self._center_window()
    
    def _center_window(self):
        """Centra la ventana en la pantalla."""
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _apply_styles(self):
        """Aplica los estilos CSS de la aplicación."""
        theme = Settings.get_theme()
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['BG_COLOR']};
            }}
            QLabel {{
                color: {theme['TEXT_COLOR']};
                font-family: {Settings.FONT_FAMILY};
                font-size: {Settings.FONT_SIZE_NORMAL}pt;
            }}
            QLabel#title {{
                font-size: {Settings.FONT_SIZE_TITLE}pt;
                font-weight: bold;
            }}
            QPushButton#nav_button {{
                background-color: transparent;
                color: {theme['TEXT_COLOR']};
                text-align: left;
                padding: 12px 15px;
                border-radius: 4px;
                font-size: 11pt;
            }}
            QPushButton#nav_button:hover {{
                background-color: {theme['NAV_HOVER']};
            }}
            QPushButton#nav_button_active {{
                background-color: {Settings.PRIMARY_COLOR};
                color: white;
                text-align: left;
                padding: 12px 15px;
                border-radius: 4px;
                font-size: 11pt;
            }}
            QFrame#nav_frame {{
                background-color: {theme['SIDEBAR_BG']};
                border-right: 1px solid {theme['BORDER_COLOR']};
            }}
            QFrame#content_frame {{
                background-color: {theme['BG_COLOR']};
            }}
            QStatusBar {{
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
                border-top: 1px solid {theme['BORDER_COLOR']};
            }}
            QMenuBar {{
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
            }}
            QMenuBar::item:selected {{
                background-color: {theme['NAV_HOVER']};
            }}
            QMenu {{
                background-color: {theme['CARD_BG']};
                color: {theme['TEXT_COLOR']};
                border: 1px solid {theme['BORDER_COLOR']};
            }}
            QMenu::item:selected {{
                background-color: {theme['NAV_HOVER']};
            }}
        """)
    
    def _create_stacked_widget(self):
        """Crea el widget apilado para cambiar entre vistas."""
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
    
    def _show_login(self):
        """Muestra la pantalla de login."""
        # Limpiar widgets anteriores
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        # Ocultar menú y status bar durante login
        self.menuBar().hide()
        if self.statusBar():
            self.statusBar().hide()
        
        # Crear y mostrar login
        login_view = LoginView(self.db_connection)
        login_view.login_successful.connect(self._on_login_success)
        self.stacked_widget.addWidget(login_view)
        self.stacked_widget.setCurrentWidget(login_view)
    
    def _on_login_success(self, user_data: dict):
        """Maneja el login exitoso."""
        self.current_user = user_data
        self._setup_main_interface()
    
    def _setup_main_interface(self):
        """Configura la interfaz principal después del login."""
        # Limpiar stacked widget
        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        
        # Aplicar estilos
        self._apply_styles()
        
        # Crear menú
        self._create_menu()
        
        # Crear layout principal
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Panel de navegación
        self.nav_frame = self._create_nav_panel()
        main_layout.addWidget(self.nav_frame)
        
        # Panel de contenido
        self.content_stack = QStackedWidget()
        theme = Settings.get_theme()
        self.content_stack.setStyleSheet(f"background-color: {theme['BG_COLOR']};")
        
        # Crear vistas con información del usuario para control de acceso
        self.libros_view = LibrosView(self.db_connection, self.current_user)
        self.usuarios_view = UsuariosView(self.db_connection, self.current_user)
        self.prestamos_view = PrestamosView(self.db_connection, self.current_user)
        self.ejemplares_view = EjemplaresView(self.db_connection, self.current_user)
        self.pasillo_view = PasilloView(self.db_connection, self.current_user)
        
        # Conectar señal de préstamo
        self.libros_view.loan_requested.connect(self._on_loan_requested)
        
        self.content_stack.addWidget(self.libros_view)
        self.content_stack.addWidget(self.usuarios_view)
        self.content_stack.addWidget(self.prestamos_view)
        self.content_stack.addWidget(self.ejemplares_view)
        self.content_stack.addWidget(self.pasillo_view)
        
        main_layout.addWidget(self.content_stack, 1)
        
        self.stacked_widget.addWidget(main_widget)
        self.stacked_widget.setCurrentWidget(main_widget)
        
        # Crear status bar
        self._create_status_bar()
        
        # Mostrar vista de libros por defecto
        self._show_books()
    
    def _create_nav_panel(self) -> QFrame:
        """Crea el panel de navegación."""
        nav_frame = QFrame()
        nav_frame.setObjectName("nav_frame")
        nav_frame.setFixedWidth(220)
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 15, 10, 15)
        nav_layout.setSpacing(5)
        
        # Header con usuario
        theme = Settings.get_theme()
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['USER_FRAME_BG']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(10, 10, 10, 10)
        
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 24px; background: transparent;")
        user_icon.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(user_icon)
        
        user_name = QLabel(self.current_user.get('name', 'Usuario'))
        user_name.setStyleSheet(f"""
            font-weight: bold;
            color: {theme['TEXT_COLOR']};
            background: transparent;
        """)
        user_name.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(user_name)
        
        user_role = QLabel(self.current_user.get('role', 'user').upper())
        user_role.setStyleSheet(f"""
            color: {Settings.PRIMARY_COLOR};
            font-size: 9pt;
            background: transparent;
        """)
        user_role.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(user_role)
        
        nav_layout.addWidget(user_frame)
        nav_layout.addSpacing(20)
        
        # Título de navegación
        nav_title = QLabel("MENÚ")
        nav_title.setStyleSheet(f"""
            color: {theme['TEXT_SECONDARY']};
            font-size: 9pt;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        nav_layout.addWidget(nav_title)
        nav_layout.addSpacing(5)
        
        # Botones de navegación
        self.nav_buttons = []
        
        self.nav_buttons.append(self._create_nav_button(nav_layout, "📚 Catálogo de Libros", self._show_books))
        self.nav_buttons.append(self._create_nav_button(nav_layout, "👥 Usuarios", self._show_users))
        self.nav_buttons.append(self._create_nav_button(nav_layout, "📋 Préstamos", self._show_loans))
        self.nav_buttons.append(self._create_nav_button(nav_layout, "📦 Ejemplares", self._show_copies))
        self.nav_buttons.append(self._create_nav_button(nav_layout, "🚪 Pasillos", self._show_pasillos))
        
        nav_layout.addStretch()
        
        # Botón de cambiar tema
        self.theme_btn = QPushButton("🌙 Modo Oscuro" if not Settings.DARK_MODE else "☀️ Modo Claro")
        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme['TEXT_COLOR']};
                text-align: left;
                padding: 12px 15px;
                border-radius: 4px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {theme['NAV_HOVER']};
            }}
        """)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        nav_layout.addWidget(self.theme_btn)
        
        # Botón de cerrar sesión
        logout_btn = QPushButton("🚪 Cerrar Sesión")
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Settings.ERROR_COLOR};
                text-align: left;
                padding: 12px 15px;
                border-radius: 4px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {theme['LOGOUT_HOVER']};
            }}
        """)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self._logout)
        nav_layout.addWidget(logout_btn)
        
        return nav_frame
    
    def _create_nav_button(self, layout, text: str, callback) -> QPushButton:
        """Crea un botón de navegación."""
        btn = QPushButton(text)
        btn.setObjectName("nav_button")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn
    
    def _update_nav_buttons(self, active_index: int):
        """Actualiza el estilo de los botones de navegación."""
        for i, btn in enumerate(self.nav_buttons):
            if i == active_index:
                btn.setObjectName("nav_button_active")
            else:
                btn.setObjectName("nav_button")
            btn.setStyle(btn.style())
    
    def _create_menu(self):
        """Crea la barra de menú."""
        menubar = self.menuBar()
        menubar.show()
        menubar.clear()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        
        connect_action = QAction("Conectar BD", self)
        connect_action.triggered.connect(self._connect_database)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction("Desconectar BD", self)
        disconnect_action.triggered.connect(self._disconnect_database)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction("Cerrar Sesión", self)
        logout_action.triggered.connect(self._logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")
        
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_status_bar(self):
        """Crea la barra de estado."""
        status_bar = self.statusBar()
        status_bar.show()
        status_bar.showMessage(f"Sesión iniciada como: {self.current_user.get('name', 'Usuario')}")
    
    def _update_status(self, message: str):
        """Actualiza el mensaje de la barra de estado."""
        self.statusBar().showMessage(message)
    
    def _show_books(self):
        """Muestra la vista de libros."""
        self.content_stack.setCurrentWidget(self.libros_view)
        self._update_nav_buttons(0)
        self._update_status("Catálogo de Libros")
    
    def _show_users(self):
        """Muestra la vista de usuarios."""
        self.content_stack.setCurrentWidget(self.usuarios_view)
        self._update_nav_buttons(1)
        self._update_status("Usuarios Registrados")
    
    def _show_loans(self):
        """Muestra la vista de préstamos."""
        self.content_stack.setCurrentWidget(self.prestamos_view)
        self._update_nav_buttons(2)
        self._update_status("Historial de Préstamos")
    
    def _show_copies(self):
        """Muestra la vista de ejemplares."""
        self.content_stack.setCurrentWidget(self.ejemplares_view)
        self._update_nav_buttons(3)
        self._update_status("Ejemplares de Libros")
    
    def _show_pasillos(self):
        """Muestra la vista de pasillos."""
        self.content_stack.setCurrentWidget(self.pasillo_view)
        self._update_nav_buttons(4)
        self._update_status("Gestión de Pasillos")
    
    def _connect_database(self):
        """Conecta a la base de datos."""
        success, message = self.db_connection.test_connection()
        if success:
            self.db_connection.connect()
            self._update_status("Conectado a la base de datos")
            QMessageBox.information(self, "Conexión", message)
        else:
            self._update_status("Error de conexión")
            QMessageBox.critical(self, "Error de Conexión", message)
    
    def _disconnect_database(self):
        """Desconecta de la base de datos."""
        self.db_connection.disconnect()
        self._update_status("Desconectado de la base de datos")
        QMessageBox.information(self, "Desconexión", "Se ha desconectado de la base de datos")
    
    def _logout(self):
        """Cierra la sesión actual."""
        reply = QMessageBox.question(
            self,
            "Cerrar Sesión",
            "¿Está seguro de que desea cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_user = None
            self._show_login()
    
    def _toggle_theme(self):
        """Alterna entre modo claro y oscuro."""
        Settings.toggle_theme()
        # Actualizar texto del botón
        self.theme_btn.setText("☀️ Modo Claro" if Settings.DARK_MODE else "🌙 Modo Oscuro")
        # Reconstruir interfaz para aplicar cambios
        self._setup_main_interface()
    
    def _show_about(self):
        """Muestra información sobre la aplicación."""
        QMessageBox.about(
            self,
            "Acerca de",
            f"<h2>📚 {Settings.APP_NAME}</h2>"
            f"<p>Versión: {Settings.APP_VERSION}</p>"
            f"<p>Sistema de Gestión Bibliotecaria</p>"
            f"<p>Aplicación para gestión de préstamos,<br>"
            f"usuarios y catálogo de libros.</p>"
        )
    
    def _on_loan_requested(self, book_data: dict):
        """Procesa una solicitud de préstamo."""
        from database.s_p_prestamo import SP_Prestamo
        from database.distributed_connection import DistributedConnection
        from datetime import date, timedelta
        
        try:
            # Crear instancia de SP_Prestamo
            dist_conn = DistributedConnection()
            sp_prestamo = SP_Prestamo(dist_conn)
            
            # Obtener datos del usuario actual
            user_node = self.current_user.get('node', 'FIS')
            
            # Convertir node a id_biblioteca
            user_biblioteca = '01' if user_node == 'FIS' else '02'
            
            # Para ahora usar cédula por defecto (puede mejorarse con selección)
            user_cedula = '1700000002'
            
            # Parámetros del préstamo
            isbn = book_data.get('isbn', '')
            titulo = book_data.get('title', '')
            fecha_prestamo = date.today()
            # Préstamo a 7 días
            fecha_devolucion_tope = fecha_prestamo + timedelta(days=7)
            
            # Obtener un ejemplar válido disponible para este ISBN
            try:
                query = f"SELECT TOP 1 id_ejemplar FROM Ejemplar_{user_biblioteca} WHERE ISBN = ?"
                conexion = dist_conn.get_connection(user_node)
                if not conexion.is_connected():
                    conexion.connect()
                
                with conexion.get_cursor() as cursor:
                    cursor.execute(query, (isbn,))
                    resultado = cursor.fetchone()
                    
                    if resultado:
                        id_ejemplar = resultado[0]
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"No hay ejemplares disponibles para el ISBN: {isbn}"
                        )
                        return
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Error al obtener ejemplares: {str(e)}"
                )
                return
            
            # Determinar el nodo según el usuario
            node = user_node
            
            # Insertar el préstamo
            success = sp_prestamo.insertar_prestamo(
                id_biblioteca=user_biblioteca,
                ISBN=isbn,
                id_ejemplar=id_ejemplar,
                cedula=user_cedula,
                fecha_prestamo=fecha_prestamo,
                fecha_devolucion_tope=fecha_devolucion_tope,
                node=node
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Préstamo Registrado",
                    f"✓ Préstamo registrado correctamente.\n\n"
                    f"Libro: {titulo}\n"
                    f"Ejemplar ID: {id_ejemplar}\n"
                    f"Fecha de devolución: {fecha_devolucion_tope.strftime('%Y-%m-%d')}"
                )
                # Recargar la vista de préstamos
                self.prestamos_view.load_data()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"No se pudo registrar el préstamo del libro:\n{titulo}"
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al registrar préstamo: {str(e)}"
            )
