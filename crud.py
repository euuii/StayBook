import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QMessageBox, QLineEdit
from PyQt6.QtCore import QDate
from crud_dialog import Ui_Dialog
from database import HotelDatabase, AccountDatabase


class CrudDialog(QDialog):
    def __init__(self, username, parent=None, edit_mode=False, room_data=None, reservation_data=None,
                 branch_data=None, dialog_type="room"):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        # Get database connection
        self.db = None
        if username != "Administrator":
            self.db = HotelDatabase(username)
        
        self.parent_window = parent
        self.edit_mode = edit_mode
        self.room_data = room_data
        self.reservation_data = reservation_data
        self.branch_data = branch_data
        self.dialog_type = dialog_type

        # Connect room buttons
        self.ui.addroom_btn.clicked.connect(self.add_room)
        self.ui.updateroom_btn.clicked.connect(self.update_room)

        # Connect reservation buttons
        self.ui.addreserve_btn.clicked.connect(self.add_reservation)
        self.ui.addreserve_btn_2.clicked.connect(self.update_reservation)

        # Connect branch buttons
        self.ui.btn_addBranch.clicked.connect(self.add_branch)
        self.ui.btn_updateBranch.clicked.connect(self.update_branch)

        # Setup password show/hide buttons
        self.setup_password_buttons()

        # Setup date widgets for reservations
        if dialog_type == "reservation":
            self.setup_reservation_dates()
            if not edit_mode:
                self.load_available_rooms()

        # Fill edit forms if editing
        if self.edit_mode and room_data and dialog_type == "room":
            self.fill_room_edit_form()

        if self.edit_mode and reservation_data and dialog_type == "reservation":
            self.fill_reservation_edit_form()

        if self.edit_mode and self.branch_data and dialog_type == "branch":
            self.fill_branch_edit_form()

    def setup_password_buttons(self):
        # Setup password visibility buttons
        self.showpass_icon = QIcon(f"icons/showpassword16.png")
        self.hidepass_icon = QIcon(f"icons/hidepassword16.png")

        self.ui.btn_showpass.setIcon(self.showpass_icon)
        self.ui.btn_showpass.clicked.connect(self.showpassword)

        self.ui.btn_showpass_2.setIcon(self.showpass_icon)
        self.ui.btn_showpass_2.clicked.connect(self.showpassword_2)

        self.ui.btn_showpass_3.setIcon(self.showpass_icon)
        self.ui.btn_showpass_3.clicked.connect(self.showpassword_3)

        self.ui.btn_showpass_4.setIcon(self.showpass_icon)
        self.ui.btn_showpass_4.clicked.connect(self.showpassword_4)

    def setup_reservation_dates(self):
        # Setup date pickers for reservations
        today = QDate.currentDate()
        tomorrow = today.addDays(1)
        
        # Setup check-in date for adding
        self.ui.checkindate_add.setCalendarPopup(True)
        self.ui.checkindate_add.setDate(today)
        self.ui.checkindate_add.setMinimumDate(today)
        self.ui.checkindate_add.setDisplayFormat("MMM dd, yyyy")
        
        # Setup check-out date for adding
        self.ui.checkoutdate_add.setCalendarPopup(True)
        self.ui.checkoutdate_add.setDate(tomorrow)
        self.ui.checkoutdate_add.setMinimumDate(tomorrow)
        self.ui.checkoutdate_add.setDisplayFormat("MMM dd, yyyy")
        
        # Setup check-in date for editing
        self.ui.checkindate_edit.setCalendarPopup(True)
        self.ui.checkindate_edit.setDisplayFormat("MMM dd, yyyy")
        
        # Setup check-out date for editing
        self.ui.checkoutdate_edit.setCalendarPopup(True)
        self.ui.checkoutdate_edit.setDisplayFormat("MMM dd, yyyy")

    # ============== PASSWORD VISIBILITY ==============

    def showpassword(self):
        # Toggle password visibility for branch add
        if self.ui.lineEdit_branchPass_3.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.lineEdit_branchPass_3.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.btn_showpass.setIcon(self.hidepass_icon)
        else:
            self.ui.lineEdit_branchPass_3.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.btn_showpass.setIcon(self.showpass_icon)

    def showpassword_2(self):
        # Toggle password visibility for branch add confirm
        if self.ui.lineEdit_branchConfPass_3.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.lineEdit_branchConfPass_3.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.btn_showpass_2.setIcon(self.hidepass_icon)
        else:
            self.ui.lineEdit_branchConfPass_3.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.btn_showpass_2.setIcon(self.showpass_icon)

    def showpassword_3(self):
        # Toggle password visibility for branch edit
        if self.ui.lineEdit_branchPass_2.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.lineEdit_branchPass_2.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.btn_showpass_3.setIcon(self.hidepass_icon)
        else:
            self.ui.lineEdit_branchPass_2.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.btn_showpass_3.setIcon(self.showpass_icon)

    def showpassword_4(self):
        # Toggle password visibility for branch edit confirm
        if self.ui.lineEdit_branchConfPass_2.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.lineEdit_branchConfPass_2.setEchoMode(QLineEdit.EchoMode.Normal)
            self.ui.btn_showpass_4.setIcon(self.hidepass_icon)
        else:
            self.ui.lineEdit_branchConfPass_2.setEchoMode(QLineEdit.EchoMode.Password)
            self.ui.btn_showpass_4.setIcon(self.showpass_icon)

    # ============== FILL EDIT FORMS ==============

    def fill_room_edit_form(self):
        # Fill edit form with existing room data
        self.ui.roomtype_edit.setCurrentText(self.room_data['type'])
        self.ui.price_edit.setText(str(self.room_data['price_rate']))
        self.ui.status_edit.setCurrentText(self.room_data['status'])
        self.ui.capacity_edit.setText(str(self.room_data['capacity']))
        self.ui.description_edit.setText(self.room_data['description'])

    def fill_reservation_edit_form(self):
        # Fill edit form with existing reservation data
        self.ui.name_edit.setText(self.reservation_data['guest_name'])
        self.ui.contact_edit.setText(self.reservation_data['contact'])
        self.ui.payment_edit.setCurrentText(self.reservation_data['payment_status'])

        # Load available rooms plus current room
        self.load_rooms_for_edit()
        self.ui.roomnum_edit.setCurrentText(str(self.reservation_data['room_number']))

        # Set dates
        checkin = QDate.fromString(self.reservation_data['checkin_date'], "yyyy-MM-dd")
        checkout = QDate.fromString(self.reservation_data['checkout_date'], "yyyy-MM-dd")
        self.ui.checkindate_edit.setDate(checkin)
        self.ui.checkoutdate_edit.setDate(checkout)

    def fill_branch_edit_form(self):
        # Fill edit form with existing branch data
        self.ui.lineEdit_branchName_2.setText(self.branch_data['username'])
        self.ui.lineEdit_branchPass_2.setText(self.branch_data['password'])
        self.ui.lineEdit_branchAddress_2.setText(self.branch_data['address'])
        self.ui.lineEdit_branchContact_2.setText(self.branch_data['contact'])

    # ============== LOAD DATA ==============

    def load_available_rooms(self):
        # Load available rooms into combobox
        available_rooms = self.db.get_available_rooms()
        self.ui.roomnum_add.clear()
        for room in available_rooms:
            self.ui.roomnum_add.addItem(str(room['room_number']))

    def load_rooms_for_edit(self):
        # Load available rooms plus current room
        available_rooms = self.db.get_available_rooms()
        self.ui.roomnum_edit.clear()

        # Add current room first
        self.ui.roomnum_edit.addItem(str(self.reservation_data['room_number']))

        # Add available rooms
        for room in available_rooms:
            self.ui.roomnum_edit.addItem(str(room['room_number']))

    # ============== ROOM OPERATIONS ==============

    def add_room(self):
        # Get form values
        room_type = self.ui.roomtype_add.currentText()
        price_rate = self.ui.price_add.text().strip()
        capacity = self.ui.capacity_add.text().strip()
        status = self.ui.status_add.currentText()
        description = self.ui.description_add.toPlainText().strip()

        # Validate input
        if not price_rate or not capacity:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        try:
            price_rate = float(price_rate)
            capacity = int(capacity)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Price must be a number and capacity must be a whole number")
            return

        # Add to database
        success, message = self.db.add_room(room_type, price_rate, capacity, description, status)

        if success:
            QMessageBox.information(self, "Success", message)
            if self.parent_window:
                self.parent_window.display_rooms()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    def update_room(self):
        # Get form values
        room_number = self.room_data['room_number']
        room_type = self.ui.roomtype_edit.currentText()
        price_rate = self.ui.price_edit.text().strip()
        status = self.ui.status_edit.currentText()
        capacity = self.ui.capacity_edit.text().strip()
        description = self.ui.description_edit.toPlainText().strip()

        # Validate input
        if not price_rate or not capacity:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        try:
            price_rate = float(price_rate)
            capacity = int(capacity)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Capacity must be a whole number, price must be a number")
            return

        # Update in database
        current_room = self.db.get_room_by_number(room_number)
        if current_room['status'] == "Occupied" and status != current_room['status']:
            QMessageBox.warning(self, "Cannot Edit", "Room is occupied. Please cancel the reservation first.")
            return
        success, message = self.db.update_room(room_number, room_type, price_rate, status, capacity, description)

        if success:
            QMessageBox.information(self, "Success", message)
            if self.parent_window:
                self.parent_window.display_rooms()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    # ============== RESERVATION OPERATIONS ==============

    def add_reservation(self):
        # Get form values
        guest_name = self.ui.name_add.text().strip()
        contact = self.ui.contact_add.text().strip()
        room_number = self.ui.roomnum_add.currentText()
        payment_status = self.ui.payment_add.currentText()
        checkin_qdate = self.ui.checkindate_add.date()
        checkout_qdate = self.ui.checkoutdate_add.date()

        # Validate input
        if not guest_name or not contact or not room_number:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        if not contact.isdigit():
            QMessageBox.warning(self, "Invalid Contact", "Contact must only consist of digits")
            return

        if checkout_qdate <= checkin_qdate:
            QMessageBox.warning(self, "Invalid Dates", "Check-out date must be after the check-in date.")
            return

        checkin_date = checkin_qdate.toString("yyyy-MM-dd")
        checkout_date = checkout_qdate.toString("yyyy-MM-dd")

        # Add to database
        success, message = self.db.add_reservation(guest_name, contact, room_number, checkin_date, checkout_date, payment_status)

        if success:
            QMessageBox.information(self, "Success", message)
            if self.parent_window:
                self.parent_window.display_reservations()
                self.parent_window.display_rooms()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    def update_reservation(self):
        # Get form values
        guest_id = self.reservation_data['guest_id']
        old_room_number = self.reservation_data['room_number']
        guest_name = self.ui.name_edit.text().strip()
        contact = self.ui.contact_edit.text().strip()
        room_number = self.ui.roomnum_edit.currentText()
        payment_status = self.ui.payment_edit.currentText()
        checkin_qdate = self.ui.checkindate_edit.date()
        checkout_qdate = self.ui.checkoutdate_edit.date()

        # Validate input
        if not guest_name or not contact or not room_number:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        if not contact.isdigit():
            QMessageBox.warning(self, "Invalid Contact", "Contact must only consist of digits")
            return

        if checkout_qdate <= checkin_qdate:
            QMessageBox.warning(self, "Invalid Dates", "Check-out date must be after the check-in date.")
            return

        checkin_date = checkin_qdate.toString("yyyy-MM-dd")
        checkout_date = checkout_qdate.toString("yyyy-MM-dd")

        # Update in database
        success, message = self.db.update_reservation(guest_id, guest_name, contact, room_number, checkin_date, checkout_date, payment_status, old_room_number)

        if success:
            QMessageBox.information(self, "Success", message)
            if self.parent_window:
                self.parent_window.display_reservations()
                self.parent_window.display_rooms()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    # ============== BRANCH OPERATIONS ==============

    def add_branch(self):
        # Get form values
        branch_name = self.ui.lineEdit_branchName.text().strip()
        password = self.ui.lineEdit_branchPass_3.text().strip()
        confirm_password = self.ui.lineEdit_branchConfPass_3.text().strip()
        address = self.ui.lineEdit_branchAddress.text().strip()
        contact = self.ui.lineEdit_branchContact.text().strip()

        # Validate input
        if not branch_name or not password or not confirm_password or not address or not contact:
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters")
            return
        
        if not contact.isdigit():
            QMessageBox.warning(self, "Invalid Contact", "Contact must only consist of digits")
            return

        # Add to database
        branch_db = AccountDatabase()
        success, message = branch_db.add_branch(branch_name, address, contact, password)

        if success:
            QMessageBox.information(self, "Success", message)
            if self.parent_window:
                self.parent_window.display_branches()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)

    def update_branch(self):
        # Get form values
        branch_id = self.branch_data['uid']
        branch_name = self.ui.lineEdit_branchName_2.text().strip()
        password = self.ui.lineEdit_branchPass_2.text().strip()
        confirm_password = self.ui.lineEdit_branchConfPass_2.text().strip()
        address = self.ui.lineEdit_branchAddress_2.text().strip()
        contact = self.ui.lineEdit_branchContact_2.text().strip()

        # Validate input
        if not branch_name or not password or not confirm_password or not address or not contact:
            QMessageBox.warning(self, "Invalid Input", "Please fill in all fields")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 6 characters")
            return
        
        if not contact.isdigit():
            QMessageBox.warning(self, "Invalid Contact", "Contact must only consist of digits")
            return

        # Update in database
        branch_db = AccountDatabase()
        success, message = branch_db.update_branch(branch_id, branch_name, address, contact, password)

        if success:
            QMessageBox.information(self, "Success", message)
            if self.parent_window:
                self.parent_window.display_branches()
            self.close()
        else:
            QMessageBox.warning(self, "Error", message)