import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from main_window import Ui_MainWindow


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

    # Reset all button styles to default
    def resetButtonStyles(self):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
