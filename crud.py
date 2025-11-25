import sqlite3
import os
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import QDate
from crud_dialog import Ui_Dialog
from login import AccountDatabase


class HotelDatabase:
    def __init__(self, username):
        # Initialize the database
        self.conn = None  # Connection to the database
        self.cursor = None  # Cursor to execute commands
        self.username = f"{username}.db"
        self.connect_db()

    def connect_db(self):
        try:
            if not os.path.exists("user_database"): #Checks if user_database folder exists
                os.makedirs("user_database") # Creates user_database folder if not exist

            self.conn = sqlite3.connect(f"user_database/{self.username}")  # Connect to the database based on username
            self.conn.row_factory = sqlite3.Row  # Access results by column name instead of index
            self.cursor = self.conn.cursor()  # Uses the cursor of our connection to execute commands
            self.cursor.execute("PRAGMA foreign_keys = ON") #Enable foreign key support

            # Create rooms table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms(
                    room_number INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    price_rate REAL,  
                    status TEXT DEFAULT 'Available',
                    capacity INTEGER,
                    description TEXT
                                )
                """)

            # Create reservations table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reservations(
                    guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guest_name TEXT NOT NULL,
                    contact TEXT,   
                    room_number INTEGER,
                    checkin_date TEXT,
                    checkout_date TEXT,
                    payment_status TEXT,
                    FOREIGN KEY (room_number) REFERENCES rooms(room_number)
                                )
                """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def get_all_rooms(self):
        # Get all rooms from database
        try:
            sql = "SELECT * FROM rooms"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching rooms: {e}")
            return []

    def get_available_rooms(self):
        # Get only available rooms
        try:
            sql = "SELECT * FROM rooms WHERE status = 'Available'"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching available rooms: {e}")
            return []

    def get_room_by_number(self, room_number):
        # Get a specific room by its room number
        try:
            sql = "SELECT * FROM rooms WHERE room_number = ?"
            self.cursor.execute(sql, (room_number,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching room: {e}")
            return None

    def add_room(self, room_type, price_rate, capacity, description, status):
        # Add a new room to database
        try:
            sql = "INSERT INTO rooms (type, price_rate, capacity, description, status) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(sql, (room_type, price_rate, capacity, description, status))
            self.conn.commit()
            return True, "Room added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding room: {e}"

    def update_room(self, room_number, room_type, price_rate, status, capacity, description):
        # Update an existing room in database
        try:
            sql = "UPDATE rooms SET type = ?, price_rate = ?, status = ?, capacity = ?, description = ? WHERE room_number = ?"
            self.cursor.execute(sql, (room_type, price_rate, status, capacity, description, room_number))
            self.conn.commit()
            return True, "Room updated successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error updating room: {e}"

    def update_room_status(self, room_number, status):
        # Update only the status of a room
        try:
            sql = "UPDATE rooms SET status = ? WHERE room_number = ?"
            self.cursor.execute(sql, (status, room_number))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            return False

    def delete_room(self, room_number):
        # Delete a room from database
        try:
            sql = "DELETE FROM rooms WHERE room_number = ?"
            self.cursor.execute(sql, (room_number,))
            self.conn.commit()
            return True, "Room deleted successfully"
        except sqlite3.IntegrityError as e:
            # This catches the foreign key constraint error
            self.conn.rollback()
            return False, "Room is occupied. Please cancel the reservation first."
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error deleting room: {e}"

    def get_all_reservations(self):
        # Get all reservations from database
        try:
            sql = "SELECT * FROM reservations"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching reservations: {e}")
            return []

    def get_reservation_by_id(self, guest_id):
        # Get a specific reservation by guest ID
        try:
            sql = "SELECT * FROM reservations WHERE guest_id = ?"
            self.cursor.execute(sql, (guest_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching reservation: {e}")
            return None

    def add_reservation(self, guest_name, contact, room_number, checkin_date, checkout_date, payment_status):
        # Add a new reservation to database
        try:
            sql = "INSERT INTO reservations (guest_name, contact, room_number, checkin_date, checkout_date, payment_status) VALUES (?, ?, ?, ?, ?, ?)"
            self.cursor.execute(sql, (guest_name, contact, room_number, checkin_date, checkout_date, payment_status))
            self.conn.commit()

            # Update room status to Occupied
            self.update_room_status(room_number, "Occupied")

            return True, "Reservation added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding reservation: {e}"

    def update_reservation(self, guest_id, guest_name, contact, room_number, checkin_date, checkout_date,
                           payment_status, old_room_number):
        # Update an existing reservation in database
        try:
            sql = "UPDATE reservations SET guest_name = ?, contact = ?, room_number = ?, checkin_date = ?, checkout_date = ?, payment_status = ? WHERE guest_id = ?"
            self.cursor.execute(sql, (guest_name, contact, room_number, checkin_date, checkout_date, payment_status,
                                      guest_id))
            self.conn.commit()

            # If room number changed, update the old room to Available and new room to Occupied
            if old_room_number != room_number:
                self.update_room_status(old_room_number, "Available")
                self.update_room_status(room_number, "Occupied")

            return True, "Reservation updated successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error updating reservation: {e}"

    def delete_reservation(self, guest_id):
        # Delete a reservation from database
        try:
            # First get the room number so we can update its status
            reservation = self.get_reservation_by_id(guest_id)
            if reservation:
                room_number = reservation['room_number']

                sql = "DELETE FROM reservations WHERE guest_id = ?"
                self.cursor.execute(sql, (guest_id,))
                self.conn.commit()

                # Update room status back to Available
                self.update_room_status(room_number, "Available")

                return True, "Reservation deleted successfully"
            else:
                return False, "Reservation not found"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error deleting reservation: {e}"


class CrudDialog(QDialog):
    def __init__(self, username, parent=None, edit_mode=False, room_data=None, reservation_data=None,
                 branch_data=None, dialog_type="room"):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.username = username
        self.db = HotelDatabase(username)
        self.parent_window = parent
        self.edit_mode = edit_mode
        self.room_data = room_data
        self.reservation_data = reservation_data
        self.branch_data = branch_data
        self.dialog_type = dialog_type  # "room" or "reservation"

        # Connect room buttons
        self.ui.addroom_btn.clicked.connect(self.add_room)
        self.ui.updateroom_btn.clicked.connect(self.update_room)

        # Connect reservation buttons
        self.ui.addreserve_btn.clicked.connect(self.add_reservation)
        self.ui.addreserve_btn_2.clicked.connect(self.update_reservation)

        # Connect branch buttons
        self.ui.btn_addBranch.clicked.connect(self.add_branch)
        self.ui.btn_updateBranch.clicked.connect(self.update_branch)

        # Connect cancel buttons
        self.ui.cancel_btn_3.clicked.connect(self.close)
        self.ui.cancel_btn_4.clicked.connect(self.close)
        self.ui.cancel_btn_5.clicked.connect(self.close)
        self.ui.cancel_btn_6.clicked.connect(self.close)

        # If this is a reservation dialog, make the date pickers easier to use
        if dialog_type == "reservation":
            # Get today's date
            today = QDate.currentDate()
            tomorrow = today.addDays(1)
            
            # Setup check-in date (for adding new reservation)
            self.ui.checkindate_add.setCalendarPopup(True)  # Show calendar when clicked
            self.ui.checkindate_add.setDate(today)  # Start with today
            self.ui.checkindate_add.setMinimumDate(today)  # Can't pick past dates
            self.ui.checkindate_add.setDisplayFormat("MMM dd, yyyy")  # Show "Jan 15, 2024"
            
            # Setup check-out date (for adding new reservation)
            self.ui.checkoutdate_add.setCalendarPopup(True)  # Show calendar when clicked
            self.ui.checkoutdate_add.setDate(tomorrow)  # Start with tomorrow
            self.ui.checkoutdate_add.setMinimumDate(tomorrow)  # Can't pick past and today dates
            self.ui.checkoutdate_add.setDisplayFormat("MMM dd, yyyy")  # Show "Jan 15, 2024"
            
            # Setup check-in date (for editing reservation)
            self.ui.checkindate_edit.setCalendarPopup(True)  # Show calendar when clicked
            self.ui.checkindate_edit.setDisplayFormat("MMM dd, yyyy")  # Show "Jan 15, 2024"
            
            # Setup check-out date (for editing reservation)
            self.ui.checkoutdate_edit.setCalendarPopup(True)  # Show calendar when clicked
            self.ui.checkoutdate_edit.setDisplayFormat("MMM dd, yyyy")  # Show "Jan 15, 2024"
            
            # If adding a new reservation, load available rooms
            if not edit_mode:
                self.load_available_rooms()

        # If we are in edit mode for room, fill the form with room data
        if self.edit_mode and room_data and dialog_type == "room":
            self.fill_room_edit_form()

        # If we are in edit mode for reservation, fill the form with reservation data
        if self.edit_mode and reservation_data and dialog_type == "reservation":
            self.fill_reservation_edit_form()

        # If we are in edit mode for branch, fill the form with branch data
        if self.edit_mode and self.branch_data and dialog_type == "branch":
            self.fill_branch_edit_form()

    def fill_room_edit_form(self):
        # Fill the edit form with existing room data
        self.ui.roomtype_edit.setCurrentText(self.room_data['type'])
        self.ui.price_edit.setText(str(self.room_data['price_rate']))
        self.ui.status_edit.setCurrentText(self.room_data['status'])
        self.ui.capacity_edit.setText(str(self.room_data['capacity']))
        self.ui.description_edit.setText(self.room_data['description'])

    def fill_reservation_edit_form(self):
        # Fill the edit form with existing reservation data
        self.ui.name_edit.setText(self.reservation_data['guest_name'])
        self.ui.contact_edit.setText(self.reservation_data['contact'])
        self.ui.payment_edit.setCurrentText(self.reservation_data['payment_status'])

        # Load available rooms plus the current room for editing
        self.load_rooms_for_edit()
        self.ui.roomnum_edit.setCurrentText(str(self.reservation_data['room_number']))

        # Set dates (dates are already configured in setup_date_widgets)
        checkin = QDate.fromString(self.reservation_data['checkin_date'], "yyyy-MM-dd")
        checkout = QDate.fromString(self.reservation_data['checkout_date'], "yyyy-MM-dd")
        self.ui.checkindate_edit.setDate(checkin)
        self.ui.checkoutdate_edit.setDate(checkout)

    def fill_branch_edit_form(self):
        # Fill the edit form with existing branch data
        self.ui.lineEdit_branchName_2.setText(self.branch_data['username'])
        self.ui.lineEdit_branchPass_2.setText(self.branch_data['password'])
        self.ui.lineEdit_branchAddress_2.setText(self.branch_data['address'])
        self.ui.lineEdit_branchContact_2.setText(self.branch_data['contact'])

    def load_available_rooms(self):
        # Load only available rooms into the combo box
        available_rooms = self.db.get_available_rooms()
        self.ui.roomnum_add.clear()
        for room in available_rooms:
            self.ui.roomnum_add.addItem(str(room['room_number']))

    def load_rooms_for_edit(self):
        # Load available rooms plus the current occupied room for editing
        available_rooms = self.db.get_available_rooms()
        self.ui.roomnum_edit.clear()

        # Add the currently occupied room first
        self.ui.roomnum_edit.addItem(str(self.reservation_data['room_number']))

        # Then add all available rooms
        for room in available_rooms:
            self.ui.roomnum_edit.addItem(str(room['room_number']))

    def add_room(self):
        # Get values from input fields
        room_type = self.ui.roomtype_add.currentText()
        price_rate = self.ui.price_add.text().strip()
        capacity = self.ui.capacity_add.text().strip()
        status = self.ui.status_add.currentText()
        description = self.ui.description_add.toPlainText().strip()

        # Check if fields are empty
        if not price_rate or not capacity:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        # Try to convert to numbers
        try:
            price_rate = float(price_rate)
            capacity = int(capacity)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Price must be a number and capacity must be a whole number")
            return

        # Add room to database
        success, message = self.db.add_room(room_type, price_rate, capacity, description, status)

        if success:
            QMessageBox.information(self, "Success", message)
            # Refresh the table in parent window (main window)
            if self.parent_window:
                self.parent_window.display_rooms()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    def update_room(self):
        # Get values from input fields
        room_number = self.room_data['room_number']

        room_type = self.ui.roomtype_edit.currentText()
        price_rate = self.ui.price_edit.text().strip()
        status = self.ui.status_edit.currentText()
        capacity = self.ui.capacity_edit.text().strip()
        description = self.ui.description_edit.toPlainText().strip()

        # Check if fields are empty
        if not price_rate or not capacity:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        # Try to convert to numbers
        try:
            price_rate = float(price_rate)
            capacity = int(capacity)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Capacity must be a whole number, price must be a number")
            return

        # Update room in database
        success, message = self.db.update_room(room_number, room_type, price_rate, status, capacity, description)

        if success:
            QMessageBox.information(self, "Success", message)
            # Refresh the table in parent window (main window)
            if self.parent_window:
                self.parent_window.display_rooms()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    def add_reservation(self):
        # Get values from input fields
        guest_name = self.ui.name_add.text().strip()
        contact = self.ui.contact_add.text().strip()
        room_number = self.ui.roomnum_add.currentText()
        payment_status = self.ui.payment_add.currentText()
        checkin_qdate = self.ui.checkindate_add.date()
        checkout_qdate = self.ui.checkoutdate_add.date()

        # Check if fields are empty
        if not guest_name or not contact or not room_number:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        if checkout_qdate <= checkin_qdate:
            QMessageBox.warning(self, "Invalid Dates", "Check-out date must be after the check-in date.")
            return

        checkin_date = checkin_qdate.toString("yyyy-MM-dd")
        checkout_date = checkout_qdate.toString("yyyy-MM-dd")

        # Add reservation to database
        success, message = self.db.add_reservation(guest_name, contact, room_number, checkin_date, checkout_date,
                                                   payment_status)

        if success:
            QMessageBox.information(self, "Success", message)
            # Refresh the tables in parent window
            if self.parent_window:
                self.parent_window.display_reservations()
                self.parent_window.display_rooms()  # Refresh rooms to show updated status
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    def update_reservation(self):
        # Get values from input fields
        guest_id = self.reservation_data['guest_id']
        old_room_number = self.reservation_data['room_number']

        guest_name = self.ui.name_edit.text().strip()
        contact = self.ui.contact_edit.text().strip()
        room_number = self.ui.roomnum_edit.currentText()
        payment_status = self.ui.payment_edit.currentText()
        checkin_qdate = self.ui.checkindate_edit.date()
        checkout_qdate = self.ui.checkoutdate_edit.date()

        # Check if fields are empty
        if not guest_name or not contact or not room_number:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        if checkout_qdate <= checkin_qdate:
            QMessageBox.warning(self, "Invalid Dates", "Check-out date must be after the check-in date.")
            return

        checkin_date = checkin_qdate.toString("yyyy-MM-dd")
        checkout_date = checkout_qdate.toString("yyyy-MM-dd")

        # Update reservation in database
        success, message = self.db.update_reservation(guest_id, guest_name, contact, room_number, checkin_date,
                                                      checkout_date, payment_status, old_room_number)

        if success:
            QMessageBox.information(self, "Success", message)
            # Refresh the tables in parent window
            if self.parent_window:
                self.parent_window.display_reservations()
                self.parent_window.display_rooms()  # Refresh rooms to show updated status
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    def add_branch(self):
        # Get values from input fields
        branch_name = self.ui.lineEdit_branchName.text().strip()
        password = self.ui.lineEdit_branchPass.text().strip()
        confirm_password = self.ui.lineEdit_branchConfPass.text().strip()
        address = self.ui.lineEdit_branchAddress.text().strip()
        contact = self.ui.lineEdit_branchContact.text().strip()

        # Check if fields are empty
        if not branch_name or not password or not confirm_password or not address or not contact:
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields")
            return

        # Check if passwords match
        elif password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match")
            return

        # Check password length
        elif len(password) < 8:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 6 characters")
            return

        # Add branch to database
        branch_db = AccountDatabase()
        try:
            sql = "INSERT INTO branches_table (username, address, contact, password) VALUES (?, ?, ?, ?)"
            branch_db.cursor.execute(sql, (branch_name, address, contact, password))
            branch_db.conn.commit()
            success = True
            message = "Branch added successfully"
        except Exception as e:
            branch_db.conn.rollback()
            success = False
            message = f"Error adding branch: {e}"

        if success:
            QMessageBox.information(self, "Success", message)
            # Refresh the table in parent window (main window)
            if self.parent_window:
                self.parent_window.display_branches()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    def update_branch(self):
        # Get values from input fields
        branch_id = self.branch_data['uid']
        branch_name = self.ui.lineEdit_branchName_2.text().strip()
        password = self.ui.lineEdit_branchPass_2.text().strip()
        confirm_password = self.ui.lineEdit_branchConfPass_2.text().strip()
        address = self.ui.lineEdit_branchAddress_2.text().strip()
        contact = self.ui.lineEdit_branchContact_2.text().strip()

        # Check if fields are empty
        if not branch_name or not password or not confirm_password or not address or not contact:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        # Check if passwords match
        if password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match")
            return

        # Check password length
        if len(password) < 6:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 6 characters")
            return

        # Update branch in database
        branch_db = AccountDatabase()
        try:
            sql = "UPDATE branches_table SET username = ?, address = ?, contact = ?, password = ? WHERE uid = ?"
            branch_db.cursor.execute(sql, (branch_name, address, contact, password, branch_id))
            branch_db.conn.commit()
            success = True
            message = "Branch updated successfully"
        except Exception as e:
            branch_db.conn.rollback()
            success = False
            message = f"Error updating branch: {e}"

        if success:
            QMessageBox.information(self, "Success", message)
            # Refresh the table in parent window
            if self.parent_window:
                self.parent_window.display_branches()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

