from PyQt6.QtWidgets import QMainWindow, QMessageBox
from main_window import Ui_MainWindow # halin sa main_window.py, mabuol kita ka class nga Ui_MainWindow
from login import LoginDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Keep track of nav buttons
        self.nav_buttons = [
            self.ui.dashboard_btn,
            self.ui.room_btn,
            self.ui.reserve_btn
        ]

        # --- Style definitions ---
        self.default_style = """
            QPushButton {
                background-color: white;
                color: black;
                border-radius: 10px;
                border: 2px solid rgb(255, 255, 255);
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgb(230, 230, 230);
            }
        """

        self.active_style = """
            QPushButton {
                background-color: rgb(85, 170, 255);
                color: white;
                border-radius: 10px;
                border: 2px solid rgb(85, 170, 255);
                padding: 5px;
            }
        """

        # Apply default style
        for btn in self.nav_buttons:
            btn.setStyleSheet(self.default_style)

        # Connect buttons
        self.ui.dashboard_btn.clicked.connect(self.showDashboard)
        self.ui.room_btn.clicked.connect(self.showRooms)
        self.ui.reserve_btn.clicked.connect(self.showReserve)

        # Default page
        self.showDashboard()

        # Logout button function, ma trigger and closeEvent nga method kung tum okon ja
        self.ui.logout_btn.clicked.connect(self.close)

    # Jang method nga ja is halin dun nga daan sa pyqt6, gagana ja kung i close mo mato mato ya window
    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirm logout", "Are you sure you want to log out?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)  # Buttons
        if result == QMessageBox.StandardButton.Yes:
            event.accept()
            return
        else:
            event.ignore()
            return

    def resetButtonStyles(self):
        # Reset all button styles to default
        for btn in self.nav_buttons:
            btn.setStyleSheet(self.default_style)

    def showDashboard(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Dashboard)
        self.resetButtonStyles()
        self.ui.dashboard_btn.setStyleSheet(self.active_style)

    def showRooms(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Rooms)
        self.resetButtonStyles()
        self.ui.room_btn.setStyleSheet(self.active_style)

    def showReserve(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Reserve)
        self.resetButtonStyles()
        self.ui.reserve_btn.setStyleSheet(self.active_style)