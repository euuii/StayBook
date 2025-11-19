import sys
from PyQt6.QtWidgets import QApplication, QDialog
from login import LoginDialog, init_db
from main import MainWindow

if __name__ == "__main__":
    # Initialize the database before starting the application
    init_db()
    
    # Create the application
    app = QApplication(sys.argv)

    while True: # Naka loop ja para mabalikan ta ya una nga line nga login_dialog
        # Show login dialog
        login_dialog = LoginDialog()
        if login_dialog.exec() == QDialog.DialogCode.Accepted: # sa login.py sa line 86. Jang line ngaja gahulat sa self.accept()
            # If login successful, show main window
            window = MainWindow()
            window.show()
            app.exec()  # Jang syntax ngaja means ga run ya application kag ma run lang gid,
                        # kung mag untat ja mabalik kita sa login page tungod sa while loop


        else:
            # Exit if login was cancelled
            sys.exit(0)