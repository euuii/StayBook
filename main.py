from PyQt6.QtGui import QPixmap, QIcon, QBrush, QColor
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout
from main_window import Ui_MainWindow
from crud import CrudDialog, HotelDatabase
from login import AccountDatabase 
import os

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Expand Column Width
        self.ui.tableWidget.setColumnWidth(0, 150)
        self.ui.tableWidget_3.setColumnWidth(0, 200)

        #Username for greetings
        self.username = username
        self.ui.username.setText(username.title())
        if username == "Administrator":
            self.db = None
        else:
            self.db = HotelDatabase(username)  # Connect to database

        # Connect buttons
        self.ui.room_btn.clicked.connect(self.showRooms)
        self.ui.reserve_btn.clicked.connect(self.showReserve)

        # Connect add room button
        self.ui.addroom_btn.clicked.connect(self.showAddRoomDialog)

        # Connect add reservation button
        self.ui.addreserve_btn.clicked.connect(self.showAddReservationDialog)

        # Connect add branch button
        self.ui.addbranch_btn.clicked.connect(self.showAddBranchDialog)

        # Store all data for filtering (initialize before loading data)
        self.all_rooms = []
        self.all_reservations = []
        self.all_branches = []

        # Connect search fields for real-time filtering
        self.ui.searchEdit_room.textChanged.connect(self.filter_rooms)
        self.ui.searchEdit_reserve.textChanged.connect(self.filter_reservations)
        self.ui.searchEdit_branch.textChanged.connect(self.filter_branches)

        # logo ka system
        logo = QPixmap("icons/hotel64.png")
        self.ui.logo.setPixmap(logo)

        # add room icon
        add_icon = QIcon("icons/add32.png")
        self.ui.addroom_btn.setIcon(add_icon)
        self.ui.addreserve_btn.setIcon(add_icon)
        self.ui.addbranch_btn.setIcon(add_icon)

        # add search icon
        search_icon = QPixmap("icons/search16.png")
        self.ui.searchIcon_room.setPixmap(search_icon)
        self.ui.searchIcon_reserve.setPixmap(search_icon)
        self.ui.search_icon.setPixmap(search_icon)

        # logout icon
        logout_icon = QIcon("icons/logout32white.png")
        self.ui.logout_btn.setIcon(logout_icon)

        # Logout button function
        self.ui.logout_btn.clicked.connect(self.close)

        # Default page (load data after everything is set up)
        if username == "Administrator":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Admin)
            self.display_branches()
        else:
            self.showRooms()

    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirm logout", "Are you sure you want to log out?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def showRooms(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Rooms)
        self.display_rooms()  # Show rooms when we click the Room button

    def showReserve(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Reserve)
        self.display_reservations()  # Show reservations when we click the Reserve button

    def display_rooms(self):
        # Get all rooms from database
        self.all_rooms = self.db.get_all_rooms()

        # Display all rooms (filtering will be handled by filter_rooms)
        self.filter_rooms()

    def filter_rooms(self):
        # Make sure we have data loaded, display all data from database if search bar is empty
        if not self.all_rooms:
            self.all_rooms = self.db.get_all_rooms()
        
        # Get the search text
        search_text = self.ui.searchEdit_room.text().lower().strip()

        # Clear the table first
        self.ui.tableWidget.setRowCount(0)

        # Filter rooms based on search text
        filtered_rooms = []
        for room in self.all_rooms:
            # Check if search text matches any column
            # Handle None values by converting to empty string
            room_number = str(room['room_number'] if room['room_number'] is not None else '').lower()
            room_type = str(room['type'] if room['type'] is not None else '').lower()
            price_rate = str(room['price_rate'] if room['price_rate'] is not None else '').lower()
            status = str(room['status'] if room['status'] is not None else '').lower()
            capacity = str(room['capacity'] if room['capacity'] is not None else '').lower()
            description = str(room['description'] if room['description'] is not None else '').lower()

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

            # Customized color of status from table
            status_item = QTableWidgetItem(status)
            if status == "Available":
                status_item.setBackground(QBrush(QColor(34, 177, 76)))  # Green
            elif status == "Occupied":
                status_item.setBackground(QBrush(QColor(255, 192, 0)))  # Orange
            elif status == "Maintenance":
                status_item.setBackground(QBrush(QColor(192, 0, 0)))  # Red
            status_item.setForeground(QBrush(QColor(255, 255, 255)))  # White text
            self.ui.tableWidget.setItem(row, 3, status_item)

            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(capacity))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(description))

            # Create Edit and Delete buttons for the Action column
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra space

            # Create Edit button
            edit_btn = QPushButton()
            edit_icon = QIcon("icons/edit16.png")
            edit_btn.setIcon(edit_icon)
            edit_btn.setMaximumWidth(60)
            edit_btn.clicked.connect(lambda checked, rn=room_number: self.edit_room_by_number(rn))

            # Create Delete button
            delete_btn = QPushButton()
            delete_icon = QIcon("icons/delete16.png")
            delete_btn.setIcon(delete_icon)
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
        # Make sure we have data loaded
        if not self.all_reservations:
            self.all_reservations = self.db.get_all_reservations()
        
        # Get the search text
        search_text = self.ui.searchEdit_reserve.text().lower().strip()

        # Clear the table first
        self.ui.tableWidget_2.setRowCount(0)

        # Filter reservations based on search text
        filtered_reservations = []
        for reservation in self.all_reservations:
            # Check if search text matches any column
            # Handle None values by converting to empty string
            guest_id = str(reservation['guest_id'] if reservation['guest_id'] is not None else '').lower()
            guest_name = str(reservation['guest_name'] if reservation['guest_name'] is not None else '').lower()
            contact = str(reservation['contact'] if reservation['contact'] is not None else '').lower()
            room_number = str(reservation['room_number'] if reservation['room_number'] is not None else '').lower()
            checkin_date = str(reservation['checkin_date'] if reservation['checkin_date'] is not None else '').lower()
            checkout_date = str(reservation['checkout_date'] if reservation['checkout_date'] is not None else '').lower()
            payment_status = str(reservation['payment_status'] if reservation['payment_status'] is not None else '').lower()

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

            # Set color for each data for Payment Status
            payment_status_item = QTableWidgetItem(payment_status)
            if payment_status == "Paid":
                payment_status_item.setBackground(QBrush(QColor(34, 177, 76)))  # Green
            elif payment_status == "Pending":
                payment_status_item.setBackground(QBrush(QColor(255, 192, 0)))  # Orange
            elif payment_status == "Cancelled":
                payment_status_item.setBackground(QBrush(QColor(192, 0, 0)))  # Red
            payment_status_item.setForeground(QBrush(QColor(255, 255, 255)))  # White text
            self.ui.tableWidget_2.setItem(row, 6, payment_status_item)

            # Create Edit and Delete buttons for the Action column
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra space

            # Create Edit button
            edit_btn = QPushButton()
            edit_icon = QIcon("icons/edit16.png")
            edit_btn.setIcon(edit_icon)
            edit_btn.setMaximumWidth(60)
            edit_btn.clicked.connect(lambda checked, gid=guest_id: self.edit_reservation_by_id(gid))

            # Create Delete button
            delete_btn = QPushButton()
            delete_icon = QIcon("icons/delete16.png")
            delete_btn.setIcon(delete_icon)
            delete_btn.setMaximumWidth(60)
            delete_btn.clicked.connect(lambda checked, gid=guest_id: self.delete_reservation_by_id(gid))

            # Add buttons to the layout
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Put the buttons into the Action column (column 7)
            self.ui.tableWidget_2.setCellWidget(row, 7, action_widget)

    def display_branches(self):
        # Get all branches from database
        branch_db = AccountDatabase()
        self.all_branches = branch_db.get_all_branches()

        # Display all branches (filtering will be handled by filter_branches)
        self.filter_branches()

    def filter_branches(self):
        # Make sure we have data loaded
        if not self.all_branches:
            branch_db = AccountDatabase()
            self.all_branches = branch_db.get_all_branches()

        # Get the search text
        search_text = self.ui.searchEdit_branch.text().lower().strip()

        # Clear the table first
        self.ui.tableWidget_3.setRowCount(0)

        # Filter branches based on search text
        filtered_branches = []
        for branch in self.all_branches:
            # Check if search text matches any column
            # Handle None values by converting to empty string
            username = str(branch['username'] if branch['username'] is not None else '').lower()
            password = str(branch['password'] if branch['password'] is not None else '').lower()
            address = str(branch['address'] if branch['address'] is not None else '').lower()
            contact = str(branch['contact'] if branch['contact'] is not None else '').lower()

            # If search is empty or matches any field, include this branch
            if (search_text == "" or
                    search_text in username or
                    search_text in password or
                    search_text in address or
                    search_text in contact):
                filtered_branches.append(branch)

        # Set the number of rows based on filtered branches
        self.ui.tableWidget_3.setRowCount(len(filtered_branches))

        # Loop through each filtered branch and add it to the table
        for row, branch in enumerate(filtered_branches):
            # Get the data from each column
            username = str(branch['username'])
            password = str(branch['password'])
            address = str(branch['address'])
            contact = str(branch['contact'])

            # Put the data into the table cells
            self.ui.tableWidget_3.setItem(row, 0, QTableWidgetItem(username))
            self.ui.tableWidget_3.setItem(row, 1, QTableWidgetItem(password))
            self.ui.tableWidget_3.setItem(row, 2, QTableWidgetItem(address))
            self.ui.tableWidget_3.setItem(row, 3, QTableWidgetItem(contact))

            # Create Edit and Delete buttons for the Action column
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra space

            # Create Edit button
            edit_btn = QPushButton()
            edit_icon = QIcon("icons/edit16.png")
            edit_btn.setIcon(edit_icon)
            edit_btn.setMaximumWidth(60)
            edit_btn.clicked.connect(lambda checked, bid=branch['uid']: self.edit_branch_by_id(bid))

            # Create Delete button
            delete_btn = QPushButton()
            delete_icon = QIcon("icons/delete16.png")
            delete_btn.setIcon(delete_icon)
            delete_btn.setMaximumWidth(60)
            delete_btn.clicked.connect(lambda checked, bid=branch['uid']: self.delete_branch_by_id(bid))

            # Add buttons to the layout
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Put the buttons into the Action column (column 4)
            self.ui.tableWidget_3.setCellWidget(row, 4, action_widget)

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

    def filter_branches(self):
        # Make sure we have data loaded
        if not self.all_branches:
            branch_db = AccountDatabase()
            self.all_branches = branch_db.get_all_branches()

        # Get the search text
        search_text = self.ui.searchEdit_branch.text().lower().strip()

        # Clear the table first
        self.ui.tableWidget_3.setRowCount(0)

        # Filter branches based on search text
        filtered_branches = []
        for branch in self.all_branches:
            # Check if search text matches any column
            # Handle None values by converting to empty string
            uid = str(branch['uid'] if branch['uid'] is not None else '').lower()
            name = str(branch['username'] if branch['username'] is not None else '').lower()
            address = str(branch['address'] if branch['address'] is not None else '').lower()
            contact = str(branch['contact'] if branch['contact'] is not None else '').lower()
            password = str(branch['password'] if branch['password'] is not None else '').lower()

            # If search is empty or matches any field, include this branch
            if (search_text == "" or
                    search_text in uid or
                    search_text in name or
                    search_text in address or
                    search_text in contact or
                    search_text in password):
                filtered_branches.append(branch)

        # Set the number of rows based on filtered branches
        self.ui.tableWidget_3.setRowCount(len(filtered_branches))

        # Loop through each filtered branch and add it to the table
        for row, branch in enumerate(filtered_branches):
            # Get the data from each column
            username = str(branch['username'])
            password = str(branch['password'])
            address = str(branch['address'])
            contact = str(branch['contact'])

            # Put the data into the table cells
            self.ui.tableWidget_3.setItem(row, 0, QTableWidgetItem(username))
            self.ui.tableWidget_3.setItem(row, 1, QTableWidgetItem(password))
            self.ui.tableWidget_3.setItem(row, 2, QTableWidgetItem(address))
            self.ui.tableWidget_3.setItem(row, 3, QTableWidgetItem(contact))

            # Create Edit and Delete buttons for the Action column
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra space

            # Create Edit button
            edit_btn = QPushButton()
            edit_icon = QIcon("icons/edit16.png")
            edit_btn.setIcon(edit_icon)
            edit_btn.setMaximumWidth(60)
            edit_btn.clicked.connect(lambda checked, bid=branch['uid']: self.edit_branch_by_id(bid))

            # Create Delete button
            delete_btn = QPushButton()
            delete_icon = QIcon("icons/delete16.png")
            delete_btn.setIcon(delete_icon)
            delete_btn.setMaximumWidth(60)
            delete_btn.clicked.connect(lambda checked, bid=branch['uid']: self.delete_branch_by_id(bid))

            # Add buttons to the layout
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Put the buttons into the Action column (column 4)
            self.ui.tableWidget_3.setCellWidget(row, 4, action_widget)

    def edit_branch_by_id(self, branch_id):
        # Get the branch data from database
        branch_db = AccountDatabase()
        branch = branch_db.get_branch_by_id(branch_id)

        if branch:
            old_username = branch['username']

            # Open the crud dialog in edit mode for branch
            crudDialog = CrudDialog(self.username, parent=self, edit_mode=True, branch_data=branch,
                                    dialog_type="branch")
            crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.branchedit_page)
            crudDialog.exec()

            # Get updated data after editing
            new_branch = branch_db.get_branch_by_id(branch_id)

            if new_branch and new_branch['username'] != old_username:
                old_file = f"branch_database/{old_username}.db"
                new_file = f"branch_database/{new_branch['username']}.db"

                if os.path.exists(old_file):
                    os.rename(old_file, new_file)

        else:
            QMessageBox.warning(self, "Error", "Could not find branch data")

    def delete_branch_by_id(self, branch_id):
        # Ask for confirmation
        result = QMessageBox.question(self, "Delete Branch",
                                      f"Are you sure you want to delete this branch?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if result == QMessageBox.StandardButton.Yes:
            # Delete the branch from database

            branch_db = AccountDatabase()
            branch = branch_db.get_branch_by_id(branch_id)
            success = branch_db.delete_branch(branch_id)
            branch_username = branch['username']  # Get the username from branch data
            branch_db_file = f"branch_database/{branch_username}.db"
            if success:
                if os.path.exists(branch_db_file):
                    os.remove(branch_db_file)  # Remove the file
                QMessageBox.information(self, "Success", "Branch deleted successfully")
                self.display_branches()  # Refresh the table
                
            else:
                QMessageBox.warning(self, "Error", "Error deleting branch")

    def showAddBranchDialog(self):
        # Pass the main window as parent so crud dialog can refresh the table
        crudDialog = CrudDialog(self.username, parent=self, dialog_type="branch")
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.branchadd_page)
        crudDialog.exec()
