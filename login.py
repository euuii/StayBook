import sqlite3
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QMessageBox
from login_dialog import Ui_Dialog

# SQLite database will live next to this file (no manual setup needed)
DB_PATH = Path(__file__).resolve().parent / "accounts.db"


def init_db():
    # Create the users table if the database is empty
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
    # Insert a new user record and return (success, message) for UI feedback
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
        # Runs if the username already exists in the database
        return False, "Username already exists. Please choose another one."


def validate_credentials(username: str, password: str) -> bool:
    # Check if the username exists and the provided password matches
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
        self.ui.reg_btn.clicked.connect(self.show_signup_page)
        self.ui.pushButton.clicked.connect(self.show_login_page)

        # Handle primary actions
        self.ui.login_btn.clicked.connect(self.handle_login)
        self.ui.pushButton_2.clicked.connect(self.handle_signup)

    def show_signup_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.signup_page)

    def show_login_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.login_page)

    def handle_login(self):
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

    def handle_signup(self):
        username = self.ui.lineEdit_3.text().strip()
        password = self.ui.lineEdit_4.text().strip()

        success, message = create_user(username, password)
        if success:
            QMessageBox.information(self, "Account Created", message)
            self.show_login_page()
            return

        QMessageBox.warning(self, "Sign Up Failed", message)