import sqlite3
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QMessageBox
from login_dialog import Ui_Dialog

class AccountDatabase:
    def __init__(self): #Initialize the database
        self.conn = None # Connection to the database
        self.cursor = None # Cursor to execute commands
        self.connect_db()


    def connect_db(self):
        try:
            self.conn = sqlite3.connect("accounts.db")  # Connect to the database called accounts.db
                                                        # If it doesn't exist, it will create one
            self.conn.row_factory = sqlite3.Row # Access results by column name instead of index
            self.cursor = self.conn.cursor() # Uses the cursor of our connection to execute commands

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                uid INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL)
            """)
        except sqlite3.Error as e: #Will run if there is an error
            print(f"Database connection error: {e}") #Prints the error message

    def validate_account(self, username, password):
        try:
            sql = "SELECT * FROM accounts WHERE username = ? AND password = ?" #SQL command to validate account
            self.cursor.execute(sql, (username, password))
            result = self.cursor.fetchone() # result will be true if there's a match, none if there's no match
            if result:
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
        except sqlite3.Error as e:
            return False, f"Error validating account: {e}"

    def add_account(self, username, password):
        try:
            sql = "INSERT INTO accounts (username, password) VALUES (?, ?)" #SQL command to insert account
            self.cursor.execute(sql, (username, password)) # Executes the SQL command from sql variable
            self.conn.commit() # Commits the changes to the database
            return True, "Account created successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except sqlite3.Error as e:
            self.conn.rollback() # Rollback changes if there is an error
            return False, f"Error adding account: {e}"


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__() #Initialize the parent class
        self.ui = Ui_Dialog() #Create an instance of the login dialog
        self.ui.setupUi(self) #setup the UI

        self.db = AccountDatabase() #Object of the AccountDatabase class

        # Switch between Login and Sign-up pages (stacked widget)
        self.ui.signuppage_btn.clicked.connect(self.show_signup_page)
        self.ui.loginpage_btn.clicked.connect(self.show_login_page)

        # Handle primary actions
        self.ui.login_btn.clicked.connect(self.handle_login)
        self.ui.signup_btn.clicked.connect(self.handle_signup)

        # logo ka system
        logo = QPixmap("icons/hotel64.png")
        self.ui.logo.setPixmap(logo)

    def show_signup_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.signup_page)

    def show_login_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.login_page)

    def handle_login(self):
        username = self.ui.lineEdit.text().strip()
        password = self.ui.lineEdit_2.text().strip()

        if not username or not password: #If username or password is empty
            QMessageBox.warning(
                self, "Missing Information", "Please enter both username and password."
            )
        else:
            success, message = self.db.validate_account(username, password)
            if success:
                self.accept() # Amo jang syntax ya ginahulat ka staybook.py para mag diretso sa main window
            else:
                QMessageBox.warning(self, "Login Failed", message)
        return

    def handle_signup(self):
        username = self.ui.lineEdit_3.text().strip()
        password = self.ui.lineEdit_4.text().strip()

        if not username or not password: #
            QMessageBox.warning(
                self, "Missing Information", "Please enter both username and password."
            )
        else:
            success, message = self.db.add_account(username, password)
            if success:
                QMessageBox.information(self, "Account Created", message)
                self.show_login_page()
            else:
                QMessageBox.warning(self, "Sign Up Failed", message)
        return