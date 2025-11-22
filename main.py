from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout
from main_window import Ui_MainWindow
from crud import CrudDialog, HotelDatabase


class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.username = username
        self.ui.username.setText(username.title())
        self.db = HotelDatabase(username)  # Connect to database

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

        # Connect add room button
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

        # Logout button function
        self.ui.logout_btn.clicked.connect(self.close)

    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirm logout", "Are you sure you want to log out?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

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
        self.display_rooms()  # Show rooms when we click the Room button

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

            # Create Edit and Delete buttons for the Action column
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra space

            # Create Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setMaximumWidth(60)
            edit_btn.clicked.connect(lambda checked, r=row: self.edit_room(r))

            # Create Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setMaximumWidth(60)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_room(r))

            # Add buttons to the layout
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Put the buttons into the Action column (column 6)
            self.ui.tableWidget1.setCellWidget(row, 6, action_widget)

    def edit_room(self, row):
        # Get the room number from the first column of the row
        room_number = self.ui.tableWidget1.item(row, 0).text()

        # Get the room data from database
        room = self.db.get_room_by_number(room_number)

        if room:
            # Open the crud dialog in edit mode
            crudDialog = CrudDialog(self.username, parent=self, edit_mode=True, room_data=room)
            crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.roomedit_page)
            crudDialog.exec()
        else:
            QMessageBox.warning(self, "Error", "Could not find room data")

    def delete_room(self, row):
        # Get the room number from the first column of the row
        room_number = self.ui.tableWidget1.item(row, 0).text()

        # Ask for confirmation
        result = QMessageBox.question(self, "Delete Room",
                                      f"Are you sure you want to delete room {room_number}?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if result == QMessageBox.StandardButton.Yes:
            # Delete the room from database
            success, message = self.db.delete_room(room_number)

            if success:
                QMessageBox.information(self, "Success", message)
                self.display_rooms()  # Refresh the table
            else:
                QMessageBox.warning(self, "Error", message)

    def showAddRoomDialog(self):
        # Pass the main window as parent so crud dialog can refresh the table
        crudDialog = CrudDialog(self.username, parent=self)
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.roomadd_page)
        crudDialog.exec()