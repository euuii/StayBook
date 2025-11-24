import sqlite3
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QDialog, QMessageBox, QLineEdit
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
                CREATE TABLE IF NOT EXISTS admin_table (
                    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password TEXT NOT NULL
                )
            """)
        except sqlite3.Error as e: #Will run if there is an error
            print(f"Database connection error: {e}") #Prints the error message

    def check_existing_admin(self):
        try:
            sql = "SELECT * FROM admin_table"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            if result:
                return True, "Admin exists"
            else:
                return False, "No administrator detected. Please create one."
        except sqlite3.Error as e:
            return False, f"Admin does not exist: {e}"

    def create_table_users(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users_table (
                    uid INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def validate_users(self, username, password):
        try:
            sql = "SELECT * FROM users_table WHERE username = ? AND password = ?" #SQL command to validate account
            self.cursor.execute(sql, (username, password))
            result = self.cursor.fetchone() # result will be true if there's a match, none if there's no match
            if result:
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
        except sqlite3.Error as e:
            return False, f"Error validating account: {e}"

    def create_administrator(self, password):
        try:
            sql = "INSERT INTO admin_table(password) VALUES (?)"
            self.cursor.execute(sql, (password,))
            self.conn.commit()
            return True, "Administrator Creation Successful"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error creating admin: {e}"

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__() #Initialize the parent class
        self.ui = Ui_Dialog() #Create an instance of the login dialog
        self.ui.setupUi(self) #setup the UI

        self.db = AccountDatabase()
        self.handle_check_admin()

        self.login_successful = False
        self.logged_in_username = None #Masudlan lang kung mag login dun

        # Switch between User and Admin pages (stacked widget)
        self.ui.admin_btn.clicked.connect(self.show_admin_page)
        self.ui.user_btn.clicked.connect(self.show_user_page)

        # Handle primary actions
        self.ui.login_btn.clicked.connect(self.handle_login_user)
        self.ui.createAdmin_btn.clicked.connect(self.handle_create_admin)

        # logo ka system
        logo = QPixmap("icons/hotel64.png")
        self.ui.logo.setPixmap(logo)

        # icons of user
        self.ui.pushButton_2.setIcon(QIcon("icons/userwhite24.png"))
        self.ui.user_btn.setIcon(QIcon("icons/userblack24.png"))

        # icons of admin
        self.ui.admin_btn.setIcon(QIcon("icons/adminblack24.png"))
        self.ui.pushButton_6.setIcon(QIcon("icons/adminwhite24.png"))

        # icons for username, password and show password
        self.ui.username_icon.setPixmap(QPixmap("icons/username16.png"))
        password_icon = QPixmap("icons/password16.png")
        self.ui.password_icon.setPixmap(password_icon)
        self.ui.password_icon_2.setPixmap(password_icon)
        self.ui.password_icon_3.setPixmap(password_icon)
        self.ui.password_icon_4.setPixmap(password_icon)

        # Show password function
        self.showpassword_icon = QIcon("icons/showpassword16.png")
        self.hidepassword_icon = QIcon("icons/hidepassword16.png")
        self.ui.showpassword_btn.setIcon(self.hidepassword_icon)
        self.ui.showpassword_btn.clicked.connect(self.showpassword)
        self.ui.showpassword_btn_2.setIcon(self.hidepassword_icon)
        self.ui.showpassword_btn_3.setIcon(self.hidepassword_icon)
        self.ui.showpassword_btn_4.setIcon(self.hidepassword_icon)

    def show_admin_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.admin_page)

    def show_user_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.user_page)

    def showpassword(self):
        if self.ui.userpassLogin_lineEdit.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.userpassLogin_lineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.showpassword_btn.setIcon(self.showpassword_icon)
        else:
            self.ui.userpassLogin_lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.showpassword_btn.setIcon(self.hidepassword_icon)

    def handle_login_user(self):
        username = self.ui.usernameLogin_lineEdit.text().strip()
        password = self.ui.userpassLogin_lineEdit.text().strip()

        if not username or not password: #If username or password is empty
            QMessageBox.warning(
                self, "Missing Information", "Please enter both username and password."
            )
        else:
            success, message = self.db.validate_users(username, password)
            if success:
                self.login_successful = True # Amo jang syntax ya ginahulat ka staybook.py para mag diretso sa main window
                self.logged_in_username = username
                self.close()
            else:
                QMessageBox.warning(self, "Login Failed", message)
        return

    def handle_check_admin(self):
        check, message = self.db.check_existing_admin()
        if check:
            self.show_user_page()
        else:
            self.ui.stackedWidget.setCurrentWidget(self.ui.createAdmin_page)
            QMessageBox.warning(self, "No Admin", message)

    def handle_create_admin(self):
        password = self.ui.adminPassword_lineEdit.text().strip()
        password2 = self.ui.adminPassword_lineEdit_2.text().strip()

        if not password or not password2:
            QMessageBox.warning(
                self, "Missing Information", "Please enter both password and confirm password."
            )
        elif password != password2:
            QMessageBox.warning(
                self, "Password do not match", "Confirm password is different to your password."
            )
        else:
            success, message = self.db.create_administrator(password)
            if success:
                self.db.create_table_users()
                QMessageBox.information(self, "Admin Created", message)
                self.ui.stackedWidget.setCurrentWidget(self.ui.user_page)
            else:
                QMessageBox.warning(self, "Admin Error Creating", message)
        return