import sys
from PyQt6.QtWidgets import QApplication, QDialog
from login import LoginDialog
from main import MainWindow

if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)

    while True: # Naka loop ja para mabalikan ta ya una nga line nga login_dialog
        # Login_dialog can initialize the database inside its __init__
        # Show login dialog
        if LoginDialog().exec() == QDialog.DialogCode.Accepted: # sa login.py sa line 91. Jang line ngaja gahulat sa self.accept()
            # If login successful, show main window
            MainWindow().show()
            app.exec()  # Jang syntax ngaja means ga run ya application kag ma run lang gid,
                        # kung mag untat ja mabalik kita sa login page tungod sa while loop

        else:
            # Exit if login was cancelled
            sys.exit(0)