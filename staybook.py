import sys
from PyQt6.QtWidgets import QApplication
from login import LoginDialog
from main import MainWindow

if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)

    while True: # Naka loop ja para mabalikan ta ya una nga line nga login_dialog
        login_dialog = LoginDialog() #Make an instance of LoginDialog
        # Login_dialog can initialize the database inside its __init__
        login_dialog.exec() # Show login dialog
        if login_dialog.login_successful:
            username = login_dialog.logged_in_username #Entered username from login.py
            # If login successful, show main window
            main_window = MainWindow(username) #Share username with main
            main_window.show()
            app.exec()  # Jang syntax ngaja means ga run ya application kag ma run lang gid,
                        # kung mag untat ja mabalik kita sa login page tungod sa while loop

        else:
            # Exit if login was cancelled
            sys.exit(0)