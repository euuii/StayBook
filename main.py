from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from main_window import Ui_MainWindow # halin sa main_window.py, mabuol kita ka class nga Ui_MainWindow
from crud import CrudDialog, HotelDatabase

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.username = username
        self.ui.username.setText(username.title())
        self.db = HotelDatabase(username)

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

        # Connect add room button to open crud dialog
        self.ui.addroom_btn.clicked.connect(self.showAddRoomDialog)

        # Default page
        self.showDashboard()

        # logo ka system
        logo = QPixmap("icons/hotel64.png")
        self.ui.logo.setPixmap(logo)

        # add room icon
        add_icon = QIcon("icons/add32.png")
        self.ui.addroom_btn.setIcon(add_icon)
        self.ui.addreserve_btn.setIcon(add_icon)

        # add search icon
        search_icon = QPixmap("icons/search16.png")
        self.ui.searchIcon_dashboard.setPixmap(search_icon)
        self.ui.searchIcon_room.setPixmap(search_icon)
        self.ui.searchIcon_reserve.setPixmap(search_icon)

        # logout icon
        logout_icon = QIcon("icons/logout32white.png")
        self.ui.logout_btn.setIcon(logout_icon)

        # Logout button function, ma trigger and closeEvent nga method kung tum okon ja
        self.ui.logout_btn.clicked.connect(self.close)

        # Automatically load data into the table when the window opens
        self.display_rooms()

    # Jang method nga ja is halin dun nga daan sa pyqt6, gagana ja kung i close mo mato mato ya window
    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirm logout", "Are you sure you want to log out?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)  # Buttons
        if result == QMessageBox.StandardButton.Yes:
            event.accept()
            return
        else:
            event.ignore()
            return

    def resetButtonStyles(self):
        # Reset all button styles to default
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

    def display_rooms(self):
        # Get all rooms from database
        rooms = self.db.get_all_rooms()

        # Clear the table first
        self.ui.tableWidget1.setRowCount(0)

        # Set the number of rows based on how many rooms we have
        self.ui.tableWidget1.setRowCount(len(rooms))

        # Loop through each room and add it to the table
        for row, room in enumerate(rooms):
            # Get the data from each column
            room_number = str(room['room_number'])
            room_type = str(room['type'])
            price_rate = str(room['price_rate'])
            status = str(room['status'])
            capacity = str(room['capacity'])
            description = str(room['description'])

            # Put the data into the table cells
            self.ui.tableWidget1.setItem(row, 0, QTableWidgetItem(room_number))
            self.ui.tableWidget1.setItem(row, 1, QTableWidgetItem(room_type))
            self.ui.tableWidget1.setItem(row, 2, QTableWidgetItem(price_rate))
            self.ui.tableWidget1.setItem(row, 3, QTableWidgetItem(status))
            self.ui.tableWidget1.setItem(row, 4, QTableWidgetItem(capacity))
            self.ui.tableWidget1.setItem(row, 5, QTableWidgetItem(description))

    def showAddRoomDialog(self):
        # Update this line to pass 'parent_window=self'
        crudDialog = CrudDialog(self.username, parent_window=self)
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.roomadd_page) #Show roomadd_page of CrudDialog
        crudDialog.exec() # Show dialog

    def showUpdateRoomDialog(self):
        crudDialog = CrudDialog(self.username, parent_window=self)
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.roomedit_page)
        crudDialog.exec()