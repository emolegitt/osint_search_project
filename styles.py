from PyQt5.QtGui import QColor

class Styles:
    @staticmethod
    def lighten_color(color):
        c = QColor(color)
        return QColor(min(c.red() + 40, 255), min(c.green() + 40, 255), min(c.blue() + 40, 255)).name()

    # Стили для тёмной темы
    input_style_dark = """
        QLineEdit {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px;
        }
        QLineEdit:focus {
            background: rgba(187, 134, 252, 0.3);
        }
    """
    label_style_dark = "color: #E0E0E0; background: transparent;"
    progress_style_dark = """
        QProgressBar {
            border: none;
            background: rgba(255, 255, 255, 0.1);
            height: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-family: 'Roboto';
            font-size: 12px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BB86FC, stop:1 #FF5555);
            border-radius: 10px;
        }
    """
    result_style_dark = """
        background: rgba(255, 255, 255, 0.05);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 12px;
        font-family: 'Roboto';
        font-size: 16px;
    """
    button_style = lambda self, color: f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color}, stop:1 {Styles.lighten_color(color)});
            color: white;
            padding: 12px;
            border-radius: 15px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {Styles.lighten_color(color)}, stop:1 {color});
        }}
    """

    # Стили для светлой темы
    input_style_light = """
        QLineEdit {
            background: rgba(0, 0, 0, 0.05);
            color: #333333;
            border: none;
            border-radius: 12px;
            padding: 12px;
        }
        QLineEdit:focus {
            background: rgba(187, 134, 252, 0.3);
        }
    """
    label_style_light = "color: #333333; background: transparent;"
    progress_style_light = """
        QProgressBar {
            border: none;
            background: rgba(0, 0, 0, 0.1);
            height: 20px;
            border-radius: 10px;
            text-align: center;
            color: #333333;
            font-family: 'Roboto';
            font-size: 12px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #BB86FC, stop:1 #FF5555);
            border-radius: 10px;
        }
    """
    result_style_light = """
        background: rgba(0, 0, 0, 0.05);
        color: #333333;
        border: none;
        border-radius: 15px;
        padding: 12px;
        font-family: 'Roboto';
        font-size: 16px;
    """