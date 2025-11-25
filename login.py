import sqlite3
from PyQt6.QtCore import Qt
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

    def create_administrator(self, password):
        try:
            sql = "INSERT INTO admin_table(password) VALUES (?)"
            self.cursor.execute(sql, (password,))
            self.conn.commit()
            return True, "Administrator Creation Successful"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error creating admin: {e}"

    def validate_admin(self, password):
        try:
            sql = "SELECT * FROM admin_table WHERE password = ?"
            self.cursor.execute(sql, (password,))
            result = self.cursor.fetchone()
            if result:
                return True, "Login successful"
            else:
                return False, "Invalid password. Please enter the correct credential"
        except sqlite3.Error as e:
            return False, f"Error validating admin: {e}"

    def create_table_branches(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS branches_table (
                    uid INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    address TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def get_branch_names(self):
        # Get only branch names from database
        try:
            sql = "SELECT username FROM branches_table"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting branches: {e}")
            return []

    def get_all_branches(self):
        # Get all branches from database
        try:
            sql = "SELECT * FROM branches_table"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching branches: {e}")
            return []

    def get_branch_by_id(self, uid):
        # Get a specific branch by its uid
        try:
            sql = "SELECT * FROM branches_table WHERE uid = ?"
            self.cursor.execute(sql, (uid,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching branch: {e}")
            return None

    def delete_branch(self, uid):
        # Delete a branch from database
        try:
            sql = "DELETE FROM branches_table WHERE uid = ?"
            self.cursor.execute(sql, (uid,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error deleting branch: {e}")
            return False

    def validate_branches(self, username, password):
        try:
            sql = "SELECT * FROM branches_table WHERE username = ? AND password = ?" #SQL command to validate account
            self.cursor.execute(sql, (username, password))
            result = self.cursor.fetchone() # result will be true if there's a match, none if there's no match
            if result:
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
        except sqlite3.Error as e:
            return False, f"Error validating account: {e}"

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__() #Initialize the parent class
        self.ui = Ui_Dialog() #Create an instance of the login dialog
        self.ui.setupUi(self) #setup the UI

        self.db = AccountDatabase()

        #Default page
        self.ui.stackedWidget.setCurrentWidget(self.ui.user_page)

        self.login_successful = False
        self.logged_in_username = None #Masudlan lang kung mag login dun

        # Switch between User and Admin pages (stacked widget)
        self.ui.admin_btn.clicked.connect(self.show_admin_page)
        self.ui.user_btn.clicked.connect(self.show_user_page)

        # Handle primary actions
        self.ui.createAdmin_btn.clicked.connect(self.handle_create_admin)
        self.ui.login_btn_2.clicked.connect(self.handle_login_admin)
        self.ui.login_btn.clicked.connect(self.handle_login_user)

        # logo ka system
        logo = QPixmap("icons/hotel64.png")
        self.ui.logo.setPixmap(logo)

        # icons of user
        self.ui.pushButton_2.setIcon(QIcon("icons/branchwhite24.png"))
        self.ui.user_btn.setIcon(QIcon("icons/branchblack24.png"))

        # Branch Name combobox function
        self.load_branch_combobox()
        self.ui.branch_combobox.view().setItemAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.ui.showpassword_btn.setIcon(self.showpassword_icon)
        self.ui.showpassword_btn.clicked.connect(self.showpassword)
        self.ui.showpassword_btn_2.setIcon(self.showpassword_icon)
        self.ui.showpassword_btn_2.clicked.connect(self.showpassword_2)
        self.ui.showpassword_btn_3.setIcon(self.showpassword_icon)
        self.ui.showpassword_btn_3.clicked.connect(self.showpassword_3)
        self.ui.showpassword_btn_4.setIcon(self.showpassword_icon)
        self.ui.showpassword_btn_4.clicked.connect(self.showpassword_4)

        # Determine which page to show after UI wiring is complete
        self.handle_check_admin()

    def show_admin_page(self):
        self.ui.adminPass_Login.setEchoMode(QLineEdit.EchoMode.Password)
        self.ui.showpassword_btn.setIcon(self.showpassword_icon)
        self.ui.stackedWidget.setCurrentWidget(self.ui.admin_page)

    def show_user_page(self):
        self.ui.showpassword_btn_2.setIcon(self.showpassword_icon)
        self.ui.userpassLogin_lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.ui.stackedWidget.setCurrentWidget(self.ui.user_page)

    def showpassword(self):
        if self.ui.userpassLogin_lineEdit.echoMode() == QLineEdit.EchoMode.Password:    #If echomode is password
            self.ui.userpassLogin_lineEdit.setEchoMode(QLineEdit.EchoMode.Normal)       #Make echomode to normal
            self.ui.showpassword_btn.setIcon(self.hidepassword_icon)                    #Change showpassword icon
        else:                                                                           #If echomode is normal
            self.ui.userpassLogin_lineEdit.setEchoMode(QLineEdit.EchoMode.Password)     #Make echomode to password
            self.ui.showpassword_btn.setIcon(self.showpassword_icon)                    #Change showpassword icon

    def showpassword_2(self):
        if self.ui.adminPass_Login.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.adminPass_Login.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.showpassword_btn_2.setIcon(self.hidepassword_icon)
        else:
            self.ui.adminPass_Login.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.showpassword_btn_2.setIcon(self.showpassword_icon)

    def showpassword_3(self):
        if self.ui.adminPassword_lineEdit.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.adminPassword_lineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.showpassword_btn_3.setIcon(self.hidepassword_icon)
        else:
            self.ui.adminPassword_lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.showpassword_btn_3.setIcon(self.showpassword_icon)

    def showpassword_4(self):
        if self.ui.adminPassword_lineEdit_2.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.adminPassword_lineEdit_2.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.showpassword_btn_4.setIcon(self.hidepassword_icon)
        else:
            self.ui.adminPassword_lineEdit_2.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.showpassword_btn_4.setIcon(self.showpassword_icon)

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
                self, "Password Mismatch", "Passwords do not match."
            )
        elif len(password) < 8:
            QMessageBox.warning(
                self, "Weak Password", "Password must be at least 8 characters."
            )
        else:
            success, message = self.db.create_administrator(password)
            if success:
                self.db.create_table_branches()
                QMessageBox.information(self, "Admin Created", message)
                self.ui.stackedWidget.setCurrentWidget(self.ui.user_page)
            else:
                QMessageBox.warning(self, "Admin Error Creating", message)
        return

    def handle_login_admin(self):
        password = self.ui.adminPass_Login.text().strip()
        if not password:
            QMessageBox.warning(
                self, "Missing Information", "Password field is empty. Please enter password."
            )
        else:
            success, message = self.db.validate_admin(password)
            if success:
                self.login_successful = True
                self.logged_in_username = "Administrator"
                self.close()
            else:
                QMessageBox.warning(self, "Login Failed", message)

    def load_branch_combobox(self):
        # Load only branch names into the combo box
        branch_names = self.db.get_branch_names()
        self.ui.branch_combobox.clear()  # Clear old items
        for branch in branch_names:
            self.ui.branch_combobox.addItem(branch['username'])

    def handle_login_user(self):
        username = self.ui.branch_combobox.currentText().strip()
        password = self.ui.userpassLogin_lineEdit.text().strip()

        if not username or not password: #If username or password is empty
            QMessageBox.warning(
                self, "Missing Information", "Please enter both username and password."
            )
        else:
            success, message = self.db.validate_branches(username, password)
            if success:
                self.login_successful = True # Amo jang syntax ya ginahulat ka staybook.py para mag diretso sa main window
                self.logged_in_username = username
                self.close()
            else:
                QMessageBox.warning(self, "Login Failed", message)
        return