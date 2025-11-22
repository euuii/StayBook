import sqlite3
from PyQt6.QtWidgets import QDialog, QMessageBox
from crud_dialog import Ui_Dialog

class HotelDatabase:
    def __init__(self, username):
        # Initialize the database
        self.conn = None # Connection to the database
        self.cursor = None # Cursor to execute commands
        self.username = f"{username}.db"
        self.connect_db()

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.username)  # Connect to the database based on username
            self.conn.row_factory = sqlite3.Row  # Access results by column name instead of index
            self.cursor = self.conn.cursor()  # Uses the cursor of our connection to execute commands

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

    def get_room_by_number(self, room_number):
        # Get a specific room by its room number
        try:
            sql = "SELECT * FROM rooms WHERE room_number = ?"
            self.cursor.execute(sql, (room_number,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching room: {e}")
            return None

    def add_room(self, room_type, price_rate, capacity, description):
        # Add a new room to database
        try:
            sql = "INSERT INTO rooms (type, price_rate, capacity, description) VALUES (?, ?, ?, ?)"
            self.cursor.execute(sql, (room_type, price_rate, capacity, description))
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

    def delete_room(self, room_number):
        # Delete a room from database
        try:
            sql = "DELETE FROM rooms WHERE room_number = ?"
            self.cursor.execute(sql, (room_number,))
            self.conn.commit()
            return True, "Room deleted successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error deleting room: {e}"


class CrudDialog(QDialog):
    def __init__(self, username, parent=None, edit_mode=False, room_data=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.username = username
        self.db = HotelDatabase(username)
        self.parent_window = parent
        self.edit_mode = edit_mode
        self.room_data = room_data

        # Connect add room button
        self.ui.addroom_btn.clicked.connect(self.add_room)

        # Connect update room button
        self.ui.updateroom_btn.clicked.connect(self.update_room)

        # If we are in edit mode, fill the form with room data
        if self.edit_mode and room_data:
            self.fill_edit_form()

    def fill_edit_form(self):
        # Fill the edit form with existing room data
        # Note: We don't set room number because it shouldn't be edited (it's the primary key)
        self.ui.roomtype_edit.setCurrentText(self.room_data['type'])
        self.ui.price_edit.setText(str(self.room_data['price_rate']))
        self.ui.status_edit.setCurrentText(self.room_data['status'])
        self.ui.capacity_edit.setText(str(self.room_data['capacity']))
        self.ui.description_edit.setText(self.room_data['description'])

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
        success, message = self.db.add_room(room_type, price_rate, capacity, description)

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
        # Use the room number from the data we already have (it shouldn't change anyway)
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