import sqlite3
from PyQt6.QtWidgets import QDialog, QMessageBox
from crud_dialog import Ui_Dialog

class HotelDatabase:
    def __init__(self, username): #Initialize the database
        self.conn = None # Connection to the database
        self.cursor = None # Cursor to execute commands
        self.username = f"{username}.db"
        self.connect_db()

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.username)  # Connect to the database based on username
                                                        # If it doesn't exist, it will create one
            self.conn.row_factory = sqlite3.Row  # Access results by column name instead of index
            self.cursor = self.conn.cursor()  # Uses the cursor of our connection to execute commands
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    room_number INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    price_rate REAL,
                    status TEXT DEFAULT 'Available',
                    capacity INTEGER,
                    description TEXT
                )
            """)
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

    def add_room(self, room_type, price_rate, capacity, description, status):
        try:
            self.cursor.execute("INSERT INTO rooms (type, price_rate, capacity, description, status) VALUES (?, ?, ?, ?, ?)", (room_type, price_rate, capacity, description, status))
            self.conn.commit()
            return True, "Room added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding room: {e}"

class CrudDialog(QDialog):
    def __init__(self, username, parent_window=None):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.username = username
        self.parent_window = parent_window
        self.db = HotelDatabase(username)

        self.ui.addroom_btn.clicked.connect(self.add_room) #Connect add room button

    def add_room(self):
        # Get room details from UI
        room_type = self.ui.roomtype_add.currentText()
        price_rate = self.ui.price_add.text().strip()
        capacity = self.ui.capacity_add.text().strip()
        status = self.ui.status_add.currentText()
        description = self.ui.description_add.toPlainText().strip()

        # Check if fields are empty
        if not price_rate or not capacity:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
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