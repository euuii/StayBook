from PyQt6.QtGui import QPixmap, QIcon, QBrush, QColor
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout
from main_window import Ui_MainWindow
from crud import CrudDialog
from database import HotelDatabase, AccountDatabase
import os

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Expand Column Width
        self.ui.tableWidget.setColumnWidth(0, 150)
        self.ui.tableWidget_3.setColumnWidth(0, 200)

        # Username for greetings
        self.username = username
        self.ui.username.setText(username.title())
        if username == "Administrator":
            self.db = None
        else:
            self.db = HotelDatabase(username)

        # Connect buttons
        self.ui.room_btn.clicked.connect(self.showRooms)
        self.ui.reserve_btn.clicked.connect(self.showReserve)
        self.ui.addroom_btn.clicked.connect(self.showAddRoomDialog)
        self.ui.addreserve_btn.clicked.connect(self.showAddReservationDialog)
        self.ui.addbranch_btn.clicked.connect(self.showAddBranchDialog)

        # Connect search fields for real-time filtering
        self.ui.searchEdit_room.textChanged.connect(self.filter_rooms)
        self.ui.searchEdit_reserve.textChanged.connect(self.filter_reservations)
        self.ui.searchEdit_branch.textChanged.connect(self.filter_branches)

        # Store all data for filtering
        self.all_rooms = []
        self.all_reservations = []
        self.all_branches = []

        # Set icons and logo
        self.setup_icons()

        # Logout button
        self.ui.logout_btn.clicked.connect(self.close)

        # Default page
        if username == "Administrator":
            self.ui.stackedWidget.setCurrentWidget(self.ui.Admin)
            self.display_branches()
        else:
            self.showRooms()

    def setup_icons(self):
        # Set logo
        logo = QPixmap("icons/hotel64.png")
        self.ui.logo.setPixmap(logo)

        # Set add icons
        add_icon = QIcon("icons/add32.png")
        self.ui.addroom_btn.setIcon(add_icon)
        self.ui.addreserve_btn.setIcon(add_icon)
        self.ui.addbranch_btn.setIcon(add_icon)

        # Set search icons
        search_icon = QPixmap("icons/search16.png")
        self.ui.searchIcon_room.setPixmap(search_icon)
        self.ui.searchIcon_reserve.setPixmap(search_icon)
        self.ui.search_icon.setPixmap(search_icon)

        # Set logout icon
        logout_icon = QIcon("icons/logout32white.png")
        self.ui.logout_btn.setIcon(logout_icon)

    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirm logout", "Are you sure you want to log out?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if result == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    # ============== ROOMS SECTION ==============

    def showRooms(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Rooms)
        self.display_rooms()

    def display_rooms(self):
        # Get all rooms from database
        self.all_rooms = self.db.get_all_rooms()
        # Show filtered rooms
        self.filter_rooms()

    def filter_rooms(self):
        # Get search text from search box
        search_text = self.ui.searchEdit_room.text().lower().strip()

        # Clear the table
        self.ui.tableWidget.setRowCount(0)

        # Filter rooms based on search
        filtered_rooms = []
        for room in self.all_rooms:
            if self.room_match_search(room, search_text):
                filtered_rooms.append(room)

        # Set table row count
        self.ui.tableWidget.setRowCount(len(filtered_rooms))

        # Add each room to table
        for row, room in enumerate(filtered_rooms):
            # Get room data
            room_number = str(room['room_number'])
            room_type = str(room['type'])
            price_rate = str(room['price_rate'])
            status = str(room['status'])
            capacity = str(room['capacity'])
            description = str(room['description'])

            # Add room data to table
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(room_number))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(room_type))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(price_rate))

            # Add status with color
            status_item = QTableWidgetItem(status)
            self.set_status_color(status_item, status)
            self.ui.tableWidget.setItem(row, 3, status_item)

            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(capacity))
            self.ui.tableWidget.setItem(row, 5, QTableWidgetItem(description))

            # Create action buttons
            edit_btn = self.create_edit_room_button(room_number)
            delete_btn = self.create_delete_room_button(room_number)

            # Add buttons to action widget
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Add action widget to table
            self.ui.tableWidget.setCellWidget(row, 6, action_widget)

    def room_match_search(self, room, search_text):
        # Convert all room data to lowercase for searching
        room_number = str(room['room_number'] if room['room_number'] is not None else '').lower()
        room_type = str(room['type'] if room['type'] is not None else '').lower()
        price_rate = str(room['price_rate'] if room['price_rate'] is not None else '').lower()
        status = str(room['status'] if room['status'] is not None else '').lower()
        capacity = str(room['capacity'] if room['capacity'] is not None else '').lower()
        description = str(room['description'] if room['description'] is not None else '').lower()

        # If no search text, show all
        if search_text == "":
            return True

        # Check if search text found in any field
        if search_text in room_number:
            return True
        if search_text in room_type:
            return True
        if search_text in price_rate:
            return True
        if search_text in status:
            return True
        if search_text in capacity:
            return True
        if search_text in description:
            return True

        return False

    def set_status_color(self, status_item, status):
        # Set background color based on status
        if status == "Available":
            status_item.setBackground(QBrush(QColor(34, 177, 76)))  # Green
        elif status == "Occupied":
            status_item.setBackground(QBrush(QColor(255, 192, 0)))  # Orange
        elif status == "Maintenance":
            status_item.setBackground(QBrush(QColor(192, 0, 0)))  # Red

        # Set white text
        status_item.setForeground(QBrush(QColor(255, 255, 255)))

    def create_edit_room_button(self, room_number):
        # Create edit button for room
        edit_btn = QPushButton()
        edit_icon = QIcon("icons/edit16.png")
        edit_btn.setIcon(edit_icon)
        edit_btn.setMaximumWidth(60)

        # Store room number in button
        edit_btn.room_number = room_number

        # Connect button click
        edit_btn.clicked.connect(self.on_edit_room_clicked)

        return edit_btn

    def create_delete_room_button(self, room_number):
        # Create delete button for room
        delete_btn = QPushButton()
        delete_icon = QIcon("icons/delete16.png")
        delete_btn.setIcon(delete_icon)
        delete_btn.setMaximumWidth(60)

        # Store room number in button
        delete_btn.room_number = room_number

        # Connect button click
        delete_btn.clicked.connect(self.on_delete_room_clicked)

        return delete_btn

    def on_edit_room_clicked(self):
        # Get which button was clicked
        sender_button = self.sender()
        room_number = sender_button.room_number
        # Call edit method
        self.edit_room_by_number(room_number)

    def on_delete_room_clicked(self):
        # Get which button was clicked
        sender_button = self.sender()
        room_number = sender_button.room_number
        # Call delete method
        self.delete_room_by_number(room_number)

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
                self.display_rooms()
            else:
                QMessageBox.warning(self, "Error", message)

    def showAddRoomDialog(self):
        # Open add room dialog
        crudDialog = CrudDialog(self.username, parent=self, dialog_type="room")
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.roomadd_page)
        crudDialog.exec()

    # ============== RESERVATIONS SECTION ==============

    def showReserve(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.Reserve)
        self.display_reservations()

    def display_reservations(self):
        # Get all reservations from database
        self.all_reservations = self.db.get_all_reservations()
        # Show filtered reservations
        self.filter_reservations()

    def filter_reservations(self):
        # Get search text from search box
        search_text = self.ui.searchEdit_reserve.text().lower().strip()

        # Clear the table
        self.ui.tableWidget_2.setRowCount(0)

        # Filter reservations based on search
        filtered_reservations = []
        for reservation in self.all_reservations:
            if self.reservation_match_search(reservation, search_text):
                filtered_reservations.append(reservation)

        # Set table row count
        self.ui.tableWidget_2.setRowCount(len(filtered_reservations))

        # Add each reservation to table
        for row, reservation in enumerate(filtered_reservations):
            # Get reservation data
            guest_id = str(reservation['guest_id'])
            guest_name = str(reservation['guest_name'])
            contact = str(reservation['contact'])
            room_number = str(reservation['room_number'])
            checkin_date = str(reservation['checkin_date'])
            checkout_date = str(reservation['checkout_date'])
            payment_status = str(reservation['payment_status'])

            # Add reservation data to table
            self.ui.tableWidget_2.setItem(row, 0, QTableWidgetItem(guest_id))
            self.ui.tableWidget_2.setItem(row, 1, QTableWidgetItem(guest_name))
            self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(contact))
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(room_number))
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(checkin_date))
            self.ui.tableWidget_2.setItem(row, 5, QTableWidgetItem(checkout_date))

            # Add payment status with color
            payment_status_item = QTableWidgetItem(payment_status)
            self.set_payment_status_color(payment_status_item, payment_status)
            self.ui.tableWidget_2.setItem(row, 6, payment_status_item)

            # Create action buttons
            edit_btn = self.create_edit_reservation_button(guest_id)
            delete_btn = self.create_delete_reservation_button(guest_id)

            # Add buttons to action widget
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Add action widget to table
            self.ui.tableWidget_2.setCellWidget(row, 7, action_widget)

    def reservation_match_search(self, reservation, search_text):
        # Convert all reservation data to lowercase for searching
        guest_id = str(reservation['guest_id'] if reservation['guest_id'] is not None else '').lower()
        guest_name = str(reservation['guest_name'] if reservation['guest_name'] is not None else '').lower()
        contact = str(reservation['contact'] if reservation['contact'] is not None else '').lower()
        room_number = str(reservation['room_number'] if reservation['room_number'] is not None else '').lower()
        checkin_date = str(reservation['checkin_date'] if reservation['checkin_date'] is not None else '').lower()
        checkout_date = str(reservation['checkout_date'] if reservation['checkout_date'] is not None else '').lower()
        payment_status = str(reservation['payment_status'] if reservation['payment_status'] is not None else '').lower()

        # If no search text, show all
        if search_text == "":
            return True

        # Check if search text found in any field
        if search_text in guest_id:
            return True
        if search_text in guest_name:
            return True
        if search_text in contact:
            return True
        if search_text in room_number:
            return True
        if search_text in checkin_date:
            return True
        if search_text in checkout_date:
            return True
        if search_text in payment_status:
            return True

        return False

    def set_payment_status_color(self, payment_status_item, payment_status):
        # Set background color based on payment status
        if payment_status == "Paid":
            payment_status_item.setBackground(QBrush(QColor(34, 177, 76)))  # Green
        elif payment_status == "Pending":
            payment_status_item.setBackground(QBrush(QColor(255, 192, 0)))  # Orange
        elif payment_status == "Cancelled":
            payment_status_item.setBackground(QBrush(QColor(192, 0, 0)))  # Red

        # Set white text
        payment_status_item.setForeground(QBrush(QColor(255, 255, 255)))

    def create_edit_reservation_button(self, guest_id):
        # Create edit button for reservation
        edit_btn = QPushButton()
        edit_icon = QIcon("icons/edit16.png")
        edit_btn.setIcon(edit_icon)
        edit_btn.setMaximumWidth(60)

        # Store guest id in button
        edit_btn.guest_id = guest_id

        # Connect button click
        edit_btn.clicked.connect(self.on_edit_reservation_clicked)

        return edit_btn

    def create_delete_reservation_button(self, guest_id):
        # Create delete button for reservation
        delete_btn = QPushButton()
        delete_icon = QIcon("icons/delete16.png")
        delete_btn.setIcon(delete_icon)
        delete_btn.setMaximumWidth(60)

        # Store guest id in button
        delete_btn.guest_id = guest_id

        # Connect button click
        delete_btn.clicked.connect(self.on_delete_reservation_clicked)

        return delete_btn

    def on_edit_reservation_clicked(self):
        # Get which button was clicked
        sender_button = self.sender()
        guest_id = sender_button.guest_id
        # Call edit method
        self.edit_reservation_by_id(guest_id)

    def on_delete_reservation_clicked(self):
        # Get which button was clicked
        sender_button = self.sender()
        guest_id = sender_button.guest_id
        # Call delete method
        self.delete_reservation_by_id(guest_id)

    def edit_reservation_by_id(self, guest_id):
        # Get the reservation data from database
        reservation = self.db.get_reservation_by_id(guest_id)

        if reservation:
            # Open the crud dialog in edit mode
            crudDialog = CrudDialog(self.username, parent=self, edit_mode=True, reservation_data=reservation, dialog_type="reservation")
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
                self.display_reservations()
                self.display_rooms()
            else:
                QMessageBox.warning(self, "Error", message)

    def showAddReservationDialog(self):
        # Open add reservation dialog
        crudDialog = CrudDialog(self.username, parent=self, dialog_type="reservation")
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.reserveadd_page)
        crudDialog.exec()

    # ============== BRANCHES SECTION ==============

    def display_branches(self):
        # Get all branches from database
        branch_db = AccountDatabase()
        self.all_branches = branch_db.get_all_branches()
        # Show filtered branches
        self.filter_branches()

    def filter_branches(self):
        # Get search text from search box
        search_text = self.ui.searchEdit_branch.text().lower().strip()

        # Clear the table
        self.ui.tableWidget_3.setRowCount(0)

        # Filter branches based on search
        filtered_branches = []
        for branch in self.all_branches:
            if self.branch_match_search(branch, search_text):
                filtered_branches.append(branch)

        # Set table row count
        self.ui.tableWidget_3.setRowCount(len(filtered_branches))

        # Add each branch to table
        for row, branch in enumerate(filtered_branches):
            # Get branch data
            username = str(branch['username'])
            password = str(branch['password'])
            address = str(branch['address'])
            contact = str(branch['contact'])

            # Add branch data to table
            self.ui.tableWidget_3.setItem(row, 0, QTableWidgetItem(username))
            self.ui.tableWidget_3.setItem(row, 1, QTableWidgetItem(password))
            self.ui.tableWidget_3.setItem(row, 2, QTableWidgetItem(address))
            self.ui.tableWidget_3.setItem(row, 3, QTableWidgetItem(contact))

            # Create action buttons
            edit_btn = self.create_edit_branch_button(branch['uid'])
            delete_btn = self.create_delete_branch_button(branch['uid'])

            # Add buttons to action widget
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)

            # Add action widget to table
            self.ui.tableWidget_3.setCellWidget(row, 4, action_widget)

    def branch_match_search(self, branch, search_text):
        # Convert all branch data to lowercase for searching
        username = str(branch['username'] if branch['username'] is not None else '').lower()
        password = str(branch['password'] if branch['password'] is not None else '').lower()
        address = str(branch['address'] if branch['address'] is not None else '').lower()
        contact = str(branch['contact'] if branch['contact'] is not None else '').lower()

        # If no search text, show all
        if search_text == "":
            return True

        # Check if search text found in any field
        if search_text in username:
            return True
        if search_text in password:
            return True
        if search_text in address:
            return True
        if search_text in contact:
            return True

        return False

    def create_edit_branch_button(self, branch_id):
        # Create edit button for branch
        edit_btn = QPushButton()
        edit_icon = QIcon("icons/edit16.png")
        edit_btn.setIcon(edit_icon)
        edit_btn.setMaximumWidth(60)

        # Store branch id in button
        edit_btn.branch_id = branch_id

        # Connect button click
        edit_btn.clicked.connect(self.on_edit_branch_clicked)

        return edit_btn

    def create_delete_branch_button(self, branch_id):
        # Create delete button for branch
        delete_btn = QPushButton()
        delete_icon = QIcon("icons/delete16.png")
        delete_btn.setIcon(delete_icon)
        delete_btn.setMaximumWidth(60)

        # Store branch id in button
        delete_btn.branch_id = branch_id

        # Connect button click
        delete_btn.clicked.connect(self.on_delete_branch_clicked)

        return delete_btn

    def on_edit_branch_clicked(self):
        # Get which button was clicked
        sender_button = self.sender()
        branch_id = sender_button.branch_id
        # Call edit method
        self.edit_branch_by_id(branch_id)

    def on_delete_branch_clicked(self):
        # Get which button was clicked
        sender_button = self.sender()
        branch_id = sender_button.branch_id
        # Call delete method
        self.delete_branch_by_id(branch_id)

    def edit_branch_by_id(self, branch_id):
        # Get the branch data from database
        branch_db = AccountDatabase()
        branch = branch_db.get_branch_by_id(branch_id)

        if branch:
            old_username = branch['username']

            # Open the crud dialog in edit mode
            crudDialog = CrudDialog(self.username, parent=self, edit_mode=True, branch_data=branch, dialog_type="branch")
            crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.branchedit_page)
            crudDialog.exec()

            # Get updated data after editing
            new_branch = branch_db.get_branch_by_id(branch_id)

            # If username changed, rename the database file
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
            
            branch_username = branch['username']
            branch_db_file = f"branch_database/{branch_username}.db"
            
            if success:
                # Delete the branch database file
                if os.path.exists(branch_db_file):
                    os.remove(branch_db_file)
                
                QMessageBox.information(self, "Success", "Branch deleted successfully")
                self.display_branches()
            else:
                QMessageBox.warning(self, "Error", "Error deleting branch")

    def showAddBranchDialog(self):
        # Open add branch dialog
        crudDialog = CrudDialog(self.username, parent=self, dialog_type="branch")
        crudDialog.ui.stackedWidget.setCurrentWidget(crudDialog.ui.branchadd_page)
        crudDialog.exec()