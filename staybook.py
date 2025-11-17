import sys
from PyQt6.QtWidgets import QApplication, QDialog
from login import LoginDialog, init_db
from main import MainWindow

if __name__ == "__main__":
    # Initialize the database before starting the application
    init_db()
    
    # Create the application
    app = QApplication(sys.argv)

    # Show login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # If login successful, show main window
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    # Exit if login was cancelled
    sys.exit(0)