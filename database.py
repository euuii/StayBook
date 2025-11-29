import sqlite3
import os

# ============== HOTEL DATABASE ==============

class HotelDatabase:
    # This class handle all room and reservation operations
    
    def __init__(self, username):
        # Initialize the database
        self.conn = None
        self.cursor = None
        self.branch_db = f"{username}.db"
        self.connect_db()

    def connect_db(self):
        # Connect to the database
        try:
            if not os.path.exists("branch_database"):
                os.makedirs("branch_database")

            self.conn = sqlite3.connect(f"branch_database/{self.branch_db}")
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")

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

    # ========== ROOM OPERATIONS ==========

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
        # Get a specific room by room number
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
        # Update an existing room
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
            self.conn.rollback()
            return False, "Room is occupied. Please cancel the reservation first."
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error deleting room: {e}"

    # ========== RESERVATION OPERATIONS ==========

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

    def update_reservation(self, guest_id, guest_name, contact, room_number, checkin_date, checkout_date, payment_status, old_room_number):
        # Update an existing reservation
        try:
            sql = "UPDATE reservations SET guest_name = ?, contact = ?, room_number = ?, checkin_date = ?, checkout_date = ?, payment_status = ? WHERE guest_id = ?"
            self.cursor.execute(sql, (guest_name, contact, room_number, checkin_date, checkout_date, payment_status, guest_id))
            self.conn.commit()

            # If room number changed, update room status
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
            # Get the room number first
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


# ============== ACCOUNT DATABASE ==============

class AccountDatabase:
    # This class handle all admin and branch operations
    
    def __init__(self):
        # Initialize the database
        self.conn = None
        self.cursor = None
        self.connect_db()

    def connect_db(self):
        # Connect to the database
        try:
            self.conn = sqlite3.connect("accounts.db")
            self.conn.row_factory = sqlite3.Row #View rows by name instead of index
            self.cursor = self.conn.cursor()

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_table (
                    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password TEXT NOT NULL
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS branches_table (
                    uid INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    address TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    # ========== ADMIN OPERATIONS ==========

    def check_existing_admin(self):
        # Check if admin already exist
        try:
            sql = "SELECT * FROM admin_table"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            if result:
                return True, "Admin exists"
            else:
                return False, "No administrator detected. Please create one."
        except sqlite3.Error as e:
            return False, f"Admin does not exist: {e}"

    def create_administrator(self, password):
        # Create new administrator
        try:
            sql = "INSERT INTO admin_table(password) VALUES (?)"
            self.cursor.execute(sql, (password,))
            self.conn.commit()
            return True, "Administrator Creation Successful"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error creating admin: {e}"

    def validate_admin(self, password):
        # Validate admin password
        try:
            sql = "SELECT * FROM admin_table WHERE password = ?"
            self.cursor.execute(sql, (password,))
            result = self.cursor.fetchone()
            if result:
                return True, "Login successful"
            else:
                return False, "Invalid password. Please enter the correct credential"
        except sqlite3.Error as e:
            return False, f"Error validating admin: {e}"

    # ========== BRANCH OPERATIONS ==========

    def get_branch_names(self):
        # Get only branch names from database
        try:
            sql = "SELECT username FROM branches_table"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting branches: {e}")
            return []

    def get_all_branches(self):
        # Get all branches from database
        try:
            sql = "SELECT * FROM branches_table"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching branches: {e}")
            return []

    def get_branch_by_id(self, uid):
        # Get a specific branch by uid
        try:
            sql = "SELECT * FROM branches_table WHERE uid = ?"
            self.cursor.execute(sql, (uid,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching branch: {e}")
            return None

    def add_branch(self, username, address, contact, password):
        # Add a new branch to database
        try:
            sql = "INSERT INTO branches_table (username, address, contact, password) VALUES (?, ?, ?, ?)"
            self.cursor.execute(sql, (username, address, contact, password))
            self.conn.commit()
            return True, "Branch added successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error adding branch: {e}"

    def update_branch(self, uid, username, address, contact, password):
        # Update an existing branch
        try:
            sql = "UPDATE branches_table SET username = ?, address = ?, contact = ?, password = ? WHERE uid = ?"
            self.cursor.execute(sql, (username, address, contact, password, uid))
            self.conn.commit()
            return True, "Branch updated successfully"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error updating branch: {e}"

    def delete_branch(self, uid):
        # Delete a branch from database
        try:
            sql = "DELETE FROM branches_table WHERE uid = ?"
            self.cursor.execute(sql, (uid,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error deleting branch: {e}")
            return False

    def validate_branches(self, username, password):
        # Validate branch login credentials
        try:
            sql = "SELECT * FROM branches_table WHERE username = ? AND password = ?"
            self.cursor.execute(sql, (username, password))
            result = self.cursor.fetchone()
            if result:
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
        except sqlite3.Error as e:
            return False, f"Error validating account: {e}"