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
        self.ui.room_btn.clicked.connect(self.showRooms)
        self.ui.reserve_btn.clicked.connect(self.showReserve)

        # Connect add room button
        self.ui.addroom_btn.clicked.connect(self.showAddRoomDialog)

        # Connect add reservation button
        self.ui.addreserve_btn.clicked.connect(self.showAddReservationDialog)

        # Default page
        self.showRooms()

        # logo ka system
        logo = QPixmap("icons/hotel64.png")
        self.ui.logo.setPixmap(logo)

        # add room icon
        add_icon = QIcon("icons/add32.png")
        self.ui.addroom_btn.setIcon(add_icon)
        self.ui.addreserve_btn.setIcon(add_icon)

        # add search icon
        search_icon = QPixmap("icons/search16.png")
        self.ui.searchIcon_room.setPixmap(search_icon)
        self.ui.searchIcon_reserve.setPixmap(search_icon)

        # logout icon
        logout_icon = QIcon("icons/logout32white.png")
        self.ui.logout_btn.setIcon(logout_icon)

        # Logout button function
        self.ui.logout_btn.clicked.connect(self.close)

        # Connect search fields for real-time filtering
        self.ui.searchEdit_room.textChanged.connect(self.filter_rooms)
        self.ui.searchEdit_reserve.textChanged.connect(self.filter_reservations)

        # Store all data for filtering
        self.all_rooms = []
        self.all_reservations = []

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

    def showRooms(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Rooms)
        self.resetButtonStyles()
        self.ui.room_btn.setStyleSheet(self.active_style)
        self.display_rooms()  # Show rooms when we click the Room button

    def showReserve(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Reserve)
        self.resetButtonStyles()
        self.ui.reserve_btn.setStyleSheet(self.active_style)
        self.display_reservations()  # Show reservations when we click the Reserve button

    def display_rooms(self):
        # Get all rooms from database
        self.all_rooms = self.db.get_all_rooms()

        # Display all rooms (filtering will be handled by filter_rooms)
        self.filter_rooms()

    def filter_rooms(self):
        # Get the search text
        search_text = self.ui.searchEdit_room.text().lower().strip()

        # Clear the table first
        self.ui.tableWidget.setRowCount(0)

        # Filter rooms based on search text
        filtered_rooms = []
        for room in self.all_rooms:
            # Check if search text matches any column
            room_number = str(room['room_number']).lower()
            room_type = str(room['type']).lower()
            price_rate = str(room['price_rate']).lower()
            status = str(room['status']).lower()
            capacity = str(room['capacity']).lower()
            description = str(room['description']).lower()

            # If search is empty or matches any field, include this room
            if (search_text == "" or 
                search_text in room_number or 
                search_text in room_type or 
                search_text in price_rate or 
                search_text in status or 
                search_text in capacity or 
                search_text in description):
                filtered_rooms.append(room)

        # Set the number of rows based on filtered rooms
        self.ui.tableWidget.setRowCount(len(filtered_rooms))

        # Loop through each filtered room and add it to the table
        for row, room in enumerate(filtered_rooms):
            # Get the data from each column
            room_number = str(room['room_number'])
            room_type = str(room['type'])
            price_rate = str(room['price_rate'])
            status = str(room['status'])
            capacity = str(room['capacity'])
            description = str(room['description'])

            # Put the data into the table cells
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(room_number))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(room_type))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(price_rate))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(status))
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(capacity))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(description))

            # Create Edit and Delete buttons for the Action column
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra space

            # Create Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setMaximumWidth(60)
            edit_btn.clicked.connect(lambda checked, rn=room_number: self.edit_room_by_number(rn))

            # Create Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setMaximumWidth(60)
            delete_btn.clicked.connect(lambda checked, rn=room_number: self.delete_room_by_number(rn))

            # Add buttons to the layout
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Put the buttons into the Action column (column 6)
            self.ui.tableWidget.setCellWidget(row, 6, action_widget)

    def display_reservations(self):
        # Get all reservations from database
        self.all_reservations = self.db.get_all_reservations()

        # Display all reservations (filtering will be handled by filter_reservations)
        self.filter_reservations()

    def filter_reservations(self):
        # Get the search text
        search_text = self.ui.searchEdit_reserve.text().lower().strip()

        # Clear the table first
        self.ui.tableWidget_2.setRowCount(0)

        # Filter reservations based on search text
        filtered_reservations = []
        for reservation in self.all_reservations:
            # Check if search text matches any column
            guest_id = str(reservation['guest_id']).lower()
            guest_name = str(reservation['guest_name']).lower()
            contact = str(reservation['contact']).lower()
            room_number = str(reservation['room_number']).lower()
            checkin_date = str(reservation['checkin_date']).lower()
            checkout_date = str(reservation['checkout_date']).lower()
            payment_status = str(reservation['payment_status']).lower()

            # If search is empty or matches any field, include this reservation
            if (search_text == "" or 
                search_text in guest_id or 
                search_text in guest_name or 
                search_text in contact or 
                search_text in room_number or 
                search_text in checkin_date or 
                search_text in checkout_date or 
                search_text in payment_status):
                filtered_reservations.append(reservation)

        # Set the number of rows based on filtered reservations
        self.ui.tableWidget_2.setRowCount(len(filtered_reservations))

        # Loop through each filtered reservation and add it to the table
        for row, reservation in enumerate(filtered_reservations):
            # Get the data from each column
            guest_id = str(reservation['guest_id'])
            guest_name = str(reservation['guest_name'])
            contact = str(reservation['contact'])
            room_number = str(reservation['room_number'])
            checkin_date = str(reservation['checkin_date'])
            checkout_date = str(reservation['checkout_date'])
            payment_status = str(reservation['payment_status'])

            # Put the data into the table cells
            self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(guest_id))
            self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(guest_name))
            self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(contact))
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(room_number))
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(checkin_date))
            self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(checkout_date))
            self.ui.tableWidget_2.setItem(row, 6, QTableWidgetItem(payment_status))

            # Create Edit and Delete buttons for the Action column
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra space

            # Create Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setMaximumWidth(60)
            edit_btn.clicked.connect(lambda checked, gid=guest_id: self.edit_reservation_by_id(gid))

            # Create Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setMaximumWidth(60)
            delete_btn.clicked.connect(lambda checked, gid=guest_id: self.delete_reservation_by_id(gid))

            # Add buttons to the layout
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Put the buttons into the Action column (column 7)
            self.ui.tableWidget_2.setCellWidget(row, 7, action_widget)

    def edit_room_by_number(self, room_number):
        # Get the room data from database
        room = self.db.get_room_by_number(room_number)

        if room:
            # Open the crud dialog in edit mode
            crudDialog = CrudDialog(self.username, parent=self, edit_mode=True, room_data=room, dialog_type="room")
            crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.roomedit_page)
            crudDialog.exec()
        else:
            QMessageBox.warning(self, "Error", "Could not find room data")

    def delete_room_by_number(self, room_number):
        # Ask for confirmation
        result = QMessageBox.question(self, "Delete Room",
                                      f"Are you sure you want to delete room {room_number}?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if result == QMessageBox.StandardButton.Yes:
            # Delete the room from database
            success, message = self.db.delete_room(room_number)

            if success:
                QMessageBox.information(self, "Success", message)
                self.display_rooms()  # Refresh the table (this will also update all_rooms)
            else:
                QMessageBox.warning(self, "Error", message)

    def edit_reservation_by_id(self, guest_id):
        # Get the reservation data from database
        reservation = self.db.get_reservation_by_id(guest_id)

        if reservation:
            # Open the crud dialog in edit mode for reservation
            crudDialog = CrudDialog(self.username, parent=self, edit_mode=True, reservation_data=reservation,
                                    dialog_type="reservation")
            crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.page)
            crudDialog.exec()
        else:
            QMessageBox.warning(self, "Error", "Could not find reservation data")

    def delete_reservation_by_id(self, guest_id):
        # Ask for confirmation
        result = QMessageBox.question(self, "Delete Reservation",
                                      f"Are you sure you want to delete this reservation?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if result == QMessageBox.StandardButton.Yes:
            # Delete the reservation from database
            success, message = self.db.delete_reservation(guest_id)

            if success:
                QMessageBox.information(self, "Success", message)
                self.display_reservations()  # Refresh the reservations table (this will also update all_reservations)
                self.display_rooms()  # Refresh the rooms table to show updated status (this will also update all_rooms)
            else:
                QMessageBox.warning(self, "Error", message)

    def showAddRoomDialog(self):
        # Pass the main window as parent so crud dialog can refresh the table
        crudDialog = CrudDialog(self.username, parent=self, dialog_type="room")
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.roomadd_page)
        crudDialog.exec()

    def showAddReservationDialog(self):
        # Pass the main window as parent so crud dialog can refresh the tables
        crudDialog = CrudDialog(self.username, parent=self, dialog_type="reservation")
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.reserveadd_page)
        crudDialog.exec()