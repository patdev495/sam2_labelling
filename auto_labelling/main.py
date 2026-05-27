import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from auto_labelling.app.main_window import MainWindow
from auto_labelling.app.constants import APP_NAME, ORG_NAME
from auto_labelling.app.theme import STYLESHEET


def main():
    QApplication.setOrganizationName(ORG_NAME)
    QApplication.setApplicationName(APP_NAME)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
