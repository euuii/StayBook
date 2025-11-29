from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QDialog, QMessageBox, QLineEdit
from login_dialog import Ui_Dialog
from database import AccountDatabase

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Database connection
        self.db = AccountDatabase()

        # Login status
        self.login_successful = False
        self.logged_in_username = None

        # Connect buttons
        self.ui.admin_btn.clicked.connect(self.show_admin_page)
        self.ui.user_btn.clicked.connect(self.show_user_page)
        self.ui.createAdmin_btn.clicked.connect(self.handle_create_admin)
        self.ui.login_btn_2.clicked.connect(self.handle_login_admin)
        self.ui.login_btn.clicked.connect(self.handle_login_user)

        # Setup UI elements
        self.setup_icons()
        self.load_branch_combobox()

        # Show password buttons
        self.showpass_icon = QIcon(f"icons/showpassword16.png")
        self.hidepass_icon = QIcon(f"icons/hidepassword16.png")
        self.ui.showpassword_btn.setIcon(self.showpass_icon)
        self.ui.showpassword_btn.clicked.connect(self.showpassword)
        self.ui.showpassword_btn_2.setIcon(self.showpass_icon)
        self.ui.showpassword_btn_2.clicked.connect(self.showpassword_2)
        self.ui.showpassword_btn_3.setIcon(self.showpass_icon)
        self.ui.showpassword_btn_3.clicked.connect(self.showpassword_3)
        self.ui.showpassword_btn_4.setIcon(self.showpass_icon)
        self.ui.showpassword_btn_4.clicked.connect(self.showpassword_4)

        # Determine which page to show
        self.handle_check_admin()

    def setup_icons(self):
        # Set logo
        logo = QPixmap("icons/hotel64.png")
        self.ui.logo.setPixmap(logo)

        # Set branch icon
        self.ui.pushButton_2.setIcon(QIcon("icons/branchwhite24.png"))
        self.ui.user_btn.setIcon(QIcon("icons/branchblack24.png"))

        # Set admin icons
        self.ui.admin_btn.setIcon(QIcon("icons/adminblack24.png"))
        self.ui.pushButton_6.setIcon(QIcon("icons/adminwhite24.png"))

        # Set input icons
        self.ui.username_icon.setPixmap(QPixmap("icons/username16.png"))
        password_icon = QPixmap("icons/password16.png")
        self.ui.password_icon.setPixmap(password_icon)
        self.ui.password_icon_2.setPixmap(password_icon)
        self.ui.password_icon_3.setPixmap(password_icon)
        self.ui.password_icon_4.setPixmap(password_icon)

        # Set branch combobox alignment
        self.ui.branch_combobox.view().setItemAlignment(Qt.AlignmentFlag.AlignCenter)

    def show_admin_page(self):
        # Show admin login page
        self.ui.adminPass_Login.setEchoMode(QLineEdit.EchoMode.Password)
        self.ui.showpassword_btn.setIcon(self.showpass_icon)
        self.ui.stackedWidget.setCurrentWidget(self.ui.admin_page)

    def show_user_page(self):
        # Show user login page
        self.ui.showpassword_btn_2.setIcon(self.showpass_icon)
        self.ui.userpassLogin_lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.ui.stackedWidget.setCurrentWidget(self.ui.user_page)

    def showpassword(self):
        # Toggle password visibility for user login
        if self.ui.userpassLogin_lineEdit.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.userpassLogin_lineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.showpassword_btn.setIcon(self.hidepass_icon)
        else:
            self.ui.userpassLogin_lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.showpassword_btn.setIcon(self.showpass_icon)

    def showpassword_2(self):
        # Toggle password visibility for admin login
        if self.ui.adminPass_Login.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.adminPass_Login.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.showpassword_btn_2.setIcon(self.hidepass_icon)
        else:
            self.ui.adminPass_Login.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.showpassword_btn_2.setIcon(self.showpass_icon)

    def showpassword_3(self):
        # Toggle password visibility for admin create
        if self.ui.adminPassword_lineEdit.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.adminPassword_lineEdit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.showpassword_btn_3.setIcon(self.hidepass_icon)
        else:
            self.ui.adminPassword_lineEdit.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.showpassword_btn_3.setIcon(self.showpass_icon)

    def showpassword_4(self):
        # Toggle password visibility for admin create confirm
        if self.ui.adminPassword_lineEdit_2.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.adminPassword_lineEdit_2.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.showpassword_btn_4.setIcon(self.hidepass_icon)
        else:
            self.ui.adminPassword_lineEdit_2.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.showpassword_btn_4.setIcon(self.showpass_icon)

    def handle_check_admin(self):
        # Check if admin exist, if not show create admin page
        check, message = self.db.check_existing_admin()
        if check:
            self.show_user_page()
        else:
            self.ui.stackedWidget.setCurrentWidget(self.ui.createAdmin_page)
            QMessageBox.warning(self, "No Admin", message)

    def handle_create_admin(self):
        # Create new administrator
        password = self.ui.adminPassword_lineEdit.text().strip()
        password2 = self.ui.adminPassword_lineEdit_2.text().strip()

        # Validate input
        if not password or not password2:
            QMessageBox.warning(self, "Missing Information", "Please enter both password and confirm password.")
            return
        
        if len(password) < 8:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters.")
            return
        
        if password != password2:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return

        # Create admin in database
        success, message = self.db.create_administrator(password)
        if success:
            QMessageBox.information(self, "Admin Created", message)
            self.ui.stackedWidget.setCurrentWidget(self.ui.user_page)
        else:
            QMessageBox.warning(self, "Admin Error Creating", message)

    def handle_login_admin(self):
        # Handle admin login
        password = self.ui.adminPass_Login.text().strip()
        
        if not password:
            QMessageBox.warning(self, "Missing Information", "Password field is empty. Please enter password.")
            return

        # Validate admin password
        success, message = self.db.validate_admin(password)
        if success:
            self.login_successful = True
            self.logged_in_username = "Administrator"
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", message)

    def load_branch_combobox(self):
        # Load branch names into combobox
        branch_names = self.db.get_branch_names()
        self.ui.branch_combobox.clear()
        for branch in branch_names:
            self.ui.branch_combobox.addItem(branch['username'])

    def handle_login_user(self):
        # Handle user login
        username = self.ui.branch_combobox.currentText().strip()
        password = self.ui.userpassLogin_lineEdit.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Missing Information", "Please enter both username and password.")
            return

        # Validate branch credentials
        success, message = self.db.validate_branches(username, password)
        if success:
            self.login_successful = True
            self.logged_in_username = username
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", message)