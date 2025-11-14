import sqlite3
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox
from login_dialog import Ui_Dialog
from main_window import Ui_MainWindow

# SQLite database will live next to this file (no manual setup needed)
DB_PATH = Path(__file__).resolve().parent / "hotel_auth.db"


def init_db():
    # Create the users table if the database is empty.
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )
        conn.commit()


def create_user(username: str, password: str) -> tuple[bool, str]:
    # Insert a new user record and return (success, message) for UI feedback.
    if not username or not password:
        return False, "Please enter both username and password."

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
        return True, "Account created successfully. You can now log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another one."


def validate_credentials(username: str, password: str) -> bool:
    # Check if the username exists and the provided password matches.
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        )
        row = cursor.fetchone()
    if not row:
        return False
    return row[0] == password


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Switch between Login and Sign-up pages (stacked widget)
        self.ui.reg_btn.clicked.connect(self.showSignupPage)
        self.ui.pushButton.clicked.connect(self.showLoginPage)

        # Handle primary actions
        self.ui.login_btn.clicked.connect(self.handleLogin)
        self.ui.pushButton_2.clicked.connect(self.handleSignup)

    def showSignupPage(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.signup_page)

    def showLoginPage(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.login_page)

    def handleLogin(self):
        username = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_2.text().strip()

        if not username or not password:
            QMessageBox.warning(
                self, "Missing Information", "Please enter both username and password."
            )
            return

        if validate_credentials(username, password):
            self.accept()
            return

        QMessageBox.warning(
            self, "Login Failed", "Invalid username or password. Please try again."
        )

    def handleSignup(self):
        username = self.ui.lineEdit_3.text().strip()
        password = self.ui.lineEdit_4.text().strip()

        success, message = create_user(username, password)
        if success:
            QMessageBox.information(self, "Account Created", message)
            self.showLoginPage()
            return

        QMessageBox.warning(self, "Sign Up Failed", message)

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
    init_db()  # Make sure the database/table exists before anything else
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    sys.exit(0)
