from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea,
                            QProgressBar, QTabWidget, QCheckBox, QComboBox, QFileDialog, QToolButton,
                            QGraphicsDropShadowEffect)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QPoint, QSettings, QSize
from osint_search.search import SearchWorker
from osint_search.styles import Styles
from osint_search.utils import animate_title, animate_button, animate_results

class OSINTWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSINT Search Tool Pro")
        self.setGeometry(100, 100, 900, 700)
        self.setFixedSize(900, 700)

        self.dragging = False
        self.drag_position = QPoint()

        self.nickname_input = None
        self.email_input = None
        self.phone_input = None
        self.ip_input = None
        self.search_button = None
        self.clear_button = None
        self.export_button = None
        self.result_area = None
        self.progress_bar = None
        self.tor_checkbox = None
        self.tor_proxy_input = None
        self.theme_combo = None
        self.api_key_input = None
        self.tabs = None
        self.title = None
        self.worker = None
        self.sidebar = None
        self.content = None
        self.logo = None
        self.db_path_input = None
        self.db_path = None
        self.txt_path_input = None
        self.txt_path = None

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        palette = QPalette()
        gradient = QLinearGradient(0, 0, 900, 700)
        gradient.setColorAt(0, QColor("#1A1B41"))
        gradient.setColorAt(0.5, QColor("#2E1A47"))
        gradient.setColorAt(1, QColor("#4B1C71"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        main_widget.setPalette(palette)
        main_widget.setStyleSheet("border-radius: 25px;")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 0)
        main_widget.setGraphicsEffect(shadow)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            background: rgba(30, 30, 60, 0.85);
            border-top-left-radius: 25px;
            border-bottom-left-radius: 25px;
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(15)

        self.logo = QLabel("OSINT Pro")
        self.logo.setFont(QFont("Montserrat", 18, QFont.Bold))
        self.logo.setStyleSheet("color: #BB86FC; padding: 10px; background: transparent;")
        shadow_logo = QGraphicsDropShadowEffect()
        shadow_logo.setBlurRadius(15)
        shadow_logo.setColor(QColor("#BB86FC"))
        shadow_logo.setOffset(0, 0)
        self.logo.setGraphicsEffect(shadow_logo)
        sidebar_layout.addWidget(self.logo)

        menu_items = [
            ("Поиск", QIcon("icons/search.png"), lambda: self.tabs.setCurrentIndex(0)),
            ("Настройки", QIcon("icons/settings.png"), lambda: self.tabs.setCurrentIndex(1)),
            ("О программе", QIcon("icons/info.png"), self.show_about),
            ("Выход", QIcon("icons/exit.png"), self.close)
        ]

        for text, icon, callback in menu_items:
            btn = QToolButton()
            btn.setText(text)
            btn.setIcon(icon)
            btn.setIconSize(QSize(24, 24))
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            btn.setFont(QFont("Poppins", 12, QFont.Bold))
            btn.setStyleSheet("""
                QToolButton {
                    background: transparent;
                    color: #E0E0E0;
                    padding: 12px;
                    border-radius: 12px;
                    text-align: left;
                    font-size: 14px;
                }
                QToolButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BB86FC, stop:1 #FF5555);
                    color: white;
                }
            """)
            shadow_btn = QGraphicsDropShadowEffect()
            shadow_btn.setBlurRadius(10)
            shadow_btn.setColor(QColor("#BB86FC"))
            shadow_btn.setOffset(0, 0)
            btn.setGraphicsEffect(shadow_btn)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        self.content = QWidget()
        self.content.setStyleSheet("""
            background: rgba(40, 40, 80, 0.9);
            border-top-right-radius: 25px;
            border-bottom-right-radius: 25px;
        """)
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(15)

        self.title = QLabel("OSINT Search Pro")
        self.title.setFont(QFont("Montserrat", 22, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            color: #BB86FC;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 12px;
        """)
        shadow_title = QGraphicsDropShadowEffect()
        shadow_title.setBlurRadius(20)
        shadow_title.setColor(QColor("#BB86FC"))
        shadow_title.setOffset(0, 0)
        self.title.setGraphicsEffect(shadow_title)
        content_layout.addWidget(self.title)
        animate_title(self.title)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.1);
                color: #E0E0E0;
                padding: 12px 25px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                margin-right: 3px;
                font-family: 'Roboto';
                font-size: 14px;
                min-width: 100px;
                text-align: center;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BB86FC, stop:1 #FF5555);
                color: white;
            }
        """)

        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        
        for label_text, placeholder in [
            ("Никнейм:", "Введите никнейм"),
            ("Email:", "Введите email"),
            ("Телефон:", "Введите телефон (например, +79991234567)"),
            ("IP-адрес:", "Введите IP-адрес (например, 8.8.8.8)")
        ]:
            label = QLabel(label_text)
            label.setFont(QFont("Roboto", 14))
            label.setStyleSheet(Styles.label_style_dark)
            shadow_label = QGraphicsDropShadowEffect()
            shadow_label.setBlurRadius(5)
            shadow_label.setColor(QColor(0, 0, 0, 100))
            shadow_label.setOffset(0, 1)
            label.setGraphicsEffect(shadow_label)
            search_layout.addWidget(label)
            
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            line_edit.setFont(QFont("Roboto", 14))
            line_edit.setStyleSheet(Styles.input_style_dark)
            shadow_input = QGraphicsDropShadowEffect()
            shadow_input.setBlurRadius(10)
            shadow_input.setColor(QColor(0, 0, 0, 100))
            shadow_input.setOffset(0, 2)
            line_edit.setGraphicsEffect(shadow_input)
            search_layout.addWidget(line_edit)
            if label_text == "Никнейм:":
                self.nickname_input = line_edit
            elif label_text == "Email:":
                self.email_input = line_edit
            elif label_text == "Телефон:":
                self.phone_input = line_edit
            elif label_text == "IP-адрес:":
                self.ip_input = line_edit

        button_layout = QHBoxLayout()
        for text, color, callback in [
            ("Поиск", "#BB86FC", self.start_search),
            ("Очистить", "#FF5555", self.clear_fields),
            ("Экспорт", "#55FF55", self.export_results)
        ]:
            btn = QPushButton(text)
            btn.setFont(QFont("Montserrat", 14, QFont.Bold))
            btn.setStyleSheet(Styles.button_style(self, color))
            shadow_btn = QGraphicsDropShadowEffect()
            shadow_btn.setBlurRadius(15)
            shadow_btn.setColor(QColor(color))
            shadow_btn.setOffset(0, 0)
            btn.setGraphicsEffect(shadow_btn)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
            animate_button(btn)
            if text == "Поиск":
                self.search_button = btn
            elif text == "Очистить":
                self.clear_button = btn
            elif text == "Экспорт":
                self.export_button = btn

        search_layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(Styles.progress_style_dark)
        shadow_progress = QGraphicsDropShadowEffect()
        shadow_progress.setBlurRadius(10)
        shadow_progress.setColor(QColor(0, 0, 0, 100))
        shadow_progress.setOffset(0, 2)
        self.progress_bar.setGraphicsEffect(shadow_progress)
        search_layout.addWidget(self.progress_bar)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setFont(QFont("Roboto", 16))
        self.result_area.setStyleSheet(Styles.result_style_dark)
        self.result_area.setMinimumHeight(300)
        shadow_result = QGraphicsDropShadowEffect()
        shadow_result.setBlurRadius(15)
        shadow_result.setColor(QColor(0, 0, 0, 100))
        shadow_result.setOffset(0, 2)
        self.result_area.setGraphicsEffect(shadow_result)
        scroll = QScrollArea()
        scroll.setWidget(self.result_area)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        search_layout.addWidget(scroll)

        self.tabs.addTab(search_tab, "Поиск")

        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        self.tor_checkbox = QCheckBox("Использовать Tor для поиска")
        self.tor_checkbox.setFont(QFont("Roboto", 14))
        self.tor_checkbox.setStyleSheet("color: #E0E0E0; padding: 5px; background: transparent;")
        shadow_tor = QGraphicsDropShadowEffect()
        shadow_tor.setBlurRadius(5)
        shadow_tor.setColor(QColor(0, 0, 0, 100))
        shadow_tor.setOffset(0, 1)
        self.tor_checkbox.setGraphicsEffect(shadow_tor)
        settings_layout.addWidget(self.tor_checkbox)

        self.tor_proxy_input = QLineEdit()
        self.tor_proxy_input.setPlaceholderText("Tor прокси (например, socks5h://127.0.0.1:9050)")
        self.tor_proxy_input.setText("socks5h://127.0.0.1:9050")
        self.tor_proxy_input.setFont(QFont("Roboto", 14))
        self.tor_proxy_input.setStyleSheet(Styles.input_style_dark)
        shadow_proxy = QGraphicsDropShadowEffect()
        shadow_proxy.setBlurRadius(10)
        shadow_proxy.setColor(QColor(0, 0, 0, 100))
        shadow_proxy.setOffset(0, 2)
        self.tor_proxy_input.setGraphicsEffect(shadow_proxy)
        settings_layout.addWidget(QLabel("Tor прокси:", styleSheet=Styles.label_style_dark))
        settings_layout.addWidget(self.tor_proxy_input)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Тёмная тема", "Светлая тема"])
        self.theme_combo.setFont(QFont("Roboto", 14))
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.15);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        shadow_theme = QGraphicsDropShadowEffect()
        shadow_theme.setBlurRadius(10)
        shadow_theme.setColor(QColor(0, 0, 0, 100))
        shadow_theme.setOffset(0, 2)
        self.theme_combo.setGraphicsEffect(shadow_theme)
        settings_layout.addWidget(QLabel("Тема:", styleSheet=Styles.label_style_dark))
        settings_layout.addWidget(self.theme_combo)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Введите API ключ (например, для X)")
        self.api_key_input.setFont(QFont("Roboto", 14))
        self.api_key_input.setStyleSheet(Styles.input_style_dark)
        shadow_api = QGraphicsDropShadowEffect()
        shadow_api.setBlurRadius(10)
        shadow_api.setColor(QColor(0, 0, 0, 100))
        shadow_api.setOffset(0, 2)
        self.api_key_input.setGraphicsEffect(shadow_api)
        settings_layout.addWidget(QLabel("API ключ:", styleSheet=Styles.label_style_dark))
        settings_layout.addWidget(self.api_key_input)

        settings_layout.addWidget(QLabel("SQLite база данных:", styleSheet=Styles.label_style_dark))
        db_layout = QHBoxLayout()
        
        self.db_path_input = QLineEdit()
        self.db_path_input.setPlaceholderText("Путь к SQLite базе данных (.db)")
        self.db_path_input.setFont(QFont("Roboto", 14))
        self.db_path_input.setStyleSheet(Styles.input_style_dark)
        self.db_path_input.setReadOnly(True)
        shadow_db = QGraphicsDropShadowEffect()
        shadow_db.setBlurRadius(10)
        shadow_db.setColor(QColor(0, 0, 0, 100))
        shadow_db.setOffset(0, 2)
        self.db_path_input.setGraphicsEffect(shadow_db)
        db_layout.addWidget(self.db_path_input)

        select_db_btn = QPushButton("Выбрать")
        select_db_btn.setFont(QFont("Montserrat", 12, QFont.Bold))
        select_db_btn.setStyleSheet(Styles.button_style(self, "#BB86FC"))
        select_db_btn.clicked.connect(self.select_database)
        db_layout.addWidget(select_db_btn)

        create_db_btn = QPushButton("Создать")
        create_db_btn.setFont(QFont("Montserrat", 12, QFont.Bold))
        create_db_btn.setStyleSheet(Styles.button_style(self, "#55FF55"))
        create_db_btn.clicked.connect(self.create_database)
        db_layout.addWidget(create_db_btn)

        settings_layout.addLayout(db_layout)

        settings_layout.addWidget(QLabel("TXT база данных:", styleSheet=Styles.label_style_dark))
        txt_layout = QHBoxLayout()
        
        self.txt_path_input = QLineEdit()
        self.txt_path_input.setPlaceholderText("Путь к TXT базе данных (.txt)")
        self.txt_path_input.setFont(QFont("Roboto", 14))
        self.txt_path_input.setStyleSheet(Styles.input_style_dark)
        self.txt_path_input.setReadOnly(True)
        shadow_txt = QGraphicsDropShadowEffect()
        shadow_txt.setBlurRadius(10)
        shadow_txt.setColor(QColor(0, 0, 0, 100))
        shadow_txt.setOffset(0, 2)
        self.txt_path_input.setGraphicsEffect(shadow_txt)
        txt_layout.addWidget(self.txt_path_input)

        select_txt_btn = QPushButton("Выбрать")
        select_txt_btn.setFont(QFont("Montserrat", 12, QFont.Bold))
        select_txt_btn.setStyleSheet(Styles.button_style(self, "#BB86FC"))
        select_txt_btn.clicked.connect(self.select_txt_database)
        txt_layout.addWidget(select_txt_btn)

        create_txt_btn = QPushButton("Создать")
        create_txt_btn.setFont(QFont("Montserrat", 12, QFont.Bold))
        create_txt_btn.setStyleSheet(Styles.button_style(self, "#55FF55"))
        create_txt_btn.clicked.connect(self.create_txt_database)
        txt_layout.addWidget(create_txt_btn)

        settings_layout.addLayout(txt_layout)

        settings_layout.addStretch()
        self.tabs.addTab(settings_tab, "Настройки")

        content_layout.addWidget(self.tabs)

        main_layout.addWidget(self.content)

        self.load_theme()
        self.load_database_path()
        self.load_txt_path()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().y() < 50:
            self.dragging = True
            self.drag_position = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    def select_database(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать SQLite базу данных", "", "SQLite Database (*.db)")
        if file_name:
            self.db_path = file_name
            self.db_path_input.setText(file_name)
            self.save_database_path()

    def create_database(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Создать SQLite базу данных", "", "SQLite Database (*.db)")
        if file_name:
            try:
                import sqlite3
                conn = sqlite3.connect(file_name)
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_user TEXT,
                        telegram_id TEXT,
                        telegram_phone TEXT,
                        instagram_user TEXT,
                        instagram_phone TEXT,
                        instagram_password TEXT,
                        vk_id TEXT,
                        vk_phone TEXT,
                        vk_password TEXT,
                        twitter_user TEXT,
                        twitter_phone TEXT,
                        twitter_password TEXT,
                        facebook_user TEXT,
                        facebook_phone TEXT,
                        facebook_password TEXT
                    )
                """)
                conn.commit()
                conn.close()
                self.db_path = file_name
                self.db_path_input.setText(file_name)
                self.save_database_path()
            except Exception as e:
                self.result_area.setText(f"Ошибка создания SQLite базы данных: {str(e)}")

    def select_txt_database(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать TXT базу данных", "", "Text Files (*.txt)")
        if file_name:
            self.txt_path = file_name
            self.txt_path_input.setText(file_name)
            self.save_txt_path()

    def create_txt_database(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Создать TXT базу данных", "", "Text Files (*.txt)")
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    header = "telegram_user,telegram_id,telegram_phone,instagram_user,instagram_phone,instagram_password,vk_id,vk_phone,vk_password,twitter_user,twitter_phone,twitter_password,facebook_user,facebook_phone,facebook_password\n"
                    f.write(header)
                self.txt_path = file_name
                self.txt_path_input.setText(file_name)
                self.save_txt_path()
            except Exception as e:
                self.result_area.setText(f"Ошибка создания TXT базы данных: {str(e)}")

    def load_database_path(self):
        settings = QSettings("OSINTApp", "Settings")
        self.db_path = settings.value("db_path", "", type=str)
        if self.db_path:
            self.db_path_input.setText(self.db_path)

    def save_database_path(self):
        settings = QSettings("OSINTApp", "Settings")
        settings.setValue("db_path", self.db_path)

    def load_txt_path(self):
        settings = QSettings("OSINTApp", "Settings")
        self.txt_path = settings.value("txt_path", "", type=str)
        if self.txt_path:
            self.txt_path_input.setText(self.txt_path)

    def save_txt_path(self):
        settings = QSettings("OSINTApp", "Settings")
        settings.setValue("txt_path", self.txt_path)

    def load_theme(self):
        settings = QSettings("OSINTApp", "Settings")
        theme_index = settings.value("theme_index", 0, type=int)
        self.theme_combo.setCurrentIndex(theme_index)
        self.change_theme()

    def save_theme(self):
        settings = QSettings("OSINTApp", "Settings")
        settings.setValue("theme_index", self.theme_combo.currentIndex())

    def change_theme(self):
        theme = self.theme_combo.currentText()
        
        if theme == "Светлая тема":
            gradient = QLinearGradient(0, 0, 900, 700)
            gradient.setColorAt(0, QColor("#F5F5F5"))
            gradient.setColorAt(0.5, QColor("#E0E0E0"))
            gradient.setColorAt(1, QColor("#D5D5D5"))
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(gradient))
            self.centralWidget().setPalette(palette)

            self.sidebar.setStyleSheet("""
                background: rgba(220, 220, 220, 0.9);
                border-top-left-radius: 25px;
                border-bottom-left-radius: 25px;
            """)

            self.content.setStyleSheet("""
                background: rgba(245, 245, 245, 0.9);
                border-top-right-radius: 25px;
                border-bottom-right-radius: 25px;
            """)

            self.title.setStyleSheet("""
                color: #6200EA;
                background: rgba(0, 0, 0, 0.05);
                border-radius: 15px;
                padding: 12px;
            """)
            self.logo.setStyleSheet("color: #6200EA; padding: 10px; background: transparent;")

            menu_button_style = """
                QToolButton {
                    background: transparent;
                    color: #333333;
                    padding: 12px;
                    border-radius: 12px;
                    text-align: left;
                    font-size: 14px;
                }
                QToolButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BB86FC, stop:1 #FF5555);
                    color: white;
                }
            """
            for btn in self.centralWidget().findChildren(QToolButton):
                btn.setStyleSheet(menu_button_style)

            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                    border: none;
                    background: rgba(0, 0, 0, 0.05);
                    border-radius: 15px;
                }
                QTabBar::tab {
                    background: rgba(0, 0, 0, 0.1);
                    color: #333333;
                    padding: 12px 25px;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                    margin-right: 3px;
                    font-family: 'Roboto';
                    font-size: 14px;
                    min-width: 100px;
                    text-align: center;
                }
                QTabBar::tab:selected {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BB86FC, stop:1 #FF5555);
                    color: white;
                }
            """)

            self.nickname_input.setStyleSheet(Styles.input_style_light)
            self.email_input.setStyleSheet(Styles.input_style_light)
            self.phone_input.setStyleSheet(Styles.input_style_light)
            self.ip_input.setStyleSheet(Styles.input_style_light)
            self.tor_proxy_input.setStyleSheet(Styles.input_style_light)
            self.api_key_input.setStyleSheet(Styles.input_style_light)
            self.db_path_input.setStyleSheet(Styles.input_style_light)
            self.txt_path_input.setStyleSheet(Styles.input_style_light)

            for label in self.centralWidget().findChildren(QLabel):
                if label != self.title and label != self.logo:
                    label.setStyleSheet(Styles.label_style_light)

            self.search_button.setStyleSheet(Styles.button_style(self, "#BB86FC"))
            self.clear_button.setStyleSheet(Styles.button_style(self, "#FF5555"))
            self.export_button.setStyleSheet(Styles.button_style(self, "#55FF55"))

            self.result_area.setStyleSheet(Styles.result_style_light)
            self.progress_bar.setStyleSheet(Styles.progress_style_light)

            self.tor_checkbox.setStyleSheet("color: #333333; padding: 5px; background: transparent;")
            self.theme_combo.setStyleSheet("""
                QComboBox {
                    background: rgba(0, 0, 0, 0.05);
                    color: #333333;
                    border: none;
                    border-radius: 12px;
                    padding: 12px;
                }
                QComboBox::drop-down {
                    border: none;
                }
            """)

        else:
            gradient = QLinearGradient(0, 0, 900, 700)
            gradient.setColorAt(0, QColor("#1A1B41"))
            gradient.setColorAt(0.5, QColor("#2E1A47"))
            gradient.setColorAt(1, QColor("#4B1C71"))
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(gradient))
            self.centralWidget().setPalette(palette)

            self.sidebar.setStyleSheet("""
                background: rgba(30, 30, 60, 0.85);
                border-top-left-radius: 25px;
                border-bottom-left-radius: 25px;
            """)

            self.content.setStyleSheet("""
                background: rgba(40, 40, 80, 0.9);
                border-top-right-radius: 25px;
                border-bottom-right-radius: 25px;
            """)

            self.title.setStyleSheet("""
                color: #BB86FC;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 12px;
            """)
            self.logo.setStyleSheet("color: #BB86FC; padding: 10px; background: transparent;")

            menu_button_style = """
                QToolButton {
                    background: transparent;
                    color: #E0E0E0;
                    padding: 12px;
                    border-radius: 12px;
                    text-align: left;
                    font-size: 14px;
                }
                QToolButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BB86FC, stop:1 #FF5555);
                    color: white;
                }
            """
            for btn in self.centralWidget().findChildren(QToolButton):
                btn.setStyleSheet(menu_button_style)

            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                    border: none;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 15px;
                }
                QTabBar::tab {
                    background: rgba(255, 255, 255, 0.1);
                    color: #E0E0E0;
                    padding: 12px 25px;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                    margin-right: 3px;
                    font-family: 'Roboto';
                    font-size: 14px;
                    min-width: 100px;
                    text-align: center;
                }
                QTabBar::tab:selected {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BB86FC, stop:1 #FF5555);
                    color: white;
                }
            """)

            self.nickname_input.setStyleSheet(Styles.input_style_dark)
            self.email_input.setStyleSheet(Styles.input_style_dark)
            self.phone_input.setStyleSheet(Styles.input_style_dark)
            self.ip_input.setStyleSheet(Styles.input_style_dark)
            self.tor_proxy_input.setStyleSheet(Styles.input_style_dark)
            self.api_key_input.setStyleSheet(Styles.input_style_dark)
            self.db_path_input.setStyleSheet(Styles.input_style_dark)
            self.txt_path_input.setStyleSheet(Styles.input_style_dark)

            for label in self.centralWidget().findChildren(QLabel):
                if label != self.title and label != self.logo:
                    label.setStyleSheet(Styles.label_style_dark)

            self.search_button.setStyleSheet(Styles.button_style(self, "#BB86FC"))
            self.clear_button.setStyleSheet(Styles.button_style(self, "#FF5555"))
            self.export_button.setStyleSheet(Styles.button_style(self, "#55FF55"))

            self.result_area.setStyleSheet(Styles.result_style_dark)
            self.progress_bar.setStyleSheet(Styles.progress_style_dark)

            self.tor_checkbox.setStyleSheet("color: #E0E0E0; padding: 5px; background: transparent;")
            self.theme_combo.setStyleSheet("""
                QComboBox {
                    background: rgba(255, 255, 255, 0.15);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px;
                }
                QComboBox::drop-down {
                    border: none;
                }
            """)

        self.save_theme()

    def start_search(self):
        nickname = self.nickname_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        ip = self.ip_input.text()

        if not (nickname or email or phone or ip):
            self.result_area.setText("Введите хотя бы одно значение!")
            return

        self.search_button.setEnabled(False)
        self.result_area.setText("Поиск выполняется...")
        self.progress_bar.setValue(0)

        use_tor = self.tor_checkbox.isChecked()
        tor_proxy = self.tor_proxy_input.text()

        self.worker = SearchWorker(nickname, email, phone, ip, use_tor, tor_proxy, self.db_path, self.txt_path)
        self.worker.result_signal.connect(self.display_results)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished.connect(self.search_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_results(self, results):
        self.result_area.setText("\n".join(results))
        animate_results(self.result_area)

    def search_finished(self):
        self.search_button.setEnabled(True)
        self.progress_bar.setValue(100)

    def clear_fields(self):
        self.nickname_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.ip_input.clear()
        self.result_area.clear()
        self.progress_bar.setValue(0)

    def export_results(self):
        if not self.result_area.toPlainText():
            self.result_area.setText("Нечего экспортировать!")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить результаты", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(self.result_area.toPlainText())
            self.result_area.append(f"\nРезультаты экспортированы в {file_name}")

    def show_about(self):
        self.result_area.setText("OSINT Search Tool Pro\nВерсия 1.0\nДля безопасного поиска данных в интернете!\nАвтор emolegit")