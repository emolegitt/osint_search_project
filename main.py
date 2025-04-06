import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from osint_search.ui import OSINTWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/icon.png"))
    window = OSINTWindow()
    window.show()
    sys.exit(app.exec_())