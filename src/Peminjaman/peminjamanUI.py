import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                           QFrame, QSizePolicy, QCheckBox, QToolButton, QDesktopWidget,QDialog,QDateEdit,QComboBox,QLineEdit,QMessageBox)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QIcon
import sqlite3
from .peminjamanController import PeminjamanController
import datetime
from pathlib import Path

class AddPeminjamanDialog(QDialog):
    """A dialog for adding new Peminjaman records with real-time validation and user feedback."""
    def __init__(self, parent=None, available_mobil=None, available_pelanggan=None):
        super().__init__(parent)

        # Set the dialog to cover the entire screen for overlay effect
        if parent:
            self.setGeometry(parent.window().geometry())
        else:
            screen = QDesktopWidget().screenGeometry()
            self.setGeometry(screen)

        # Configure window properties for modal overlay appearance
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.controller = PeminjamanController()

        # Store options for dropdowns
        self.available_mobil = available_mobil or []
        self.available_pelanggan = available_pelanggan or []

        # Initialize validation states
        self.validation_states = {
            'Nama': False,
            'NIK': False,
            'NomorPlat': False,
            'Kontak': False,
            'TanggalPeminjaman': True,
            'TenggatPengembalian': True,
            'TenggatPembayaran': True,
            'BesarPembayaran': False
        }

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface with all components and layouts."""
        # Main layout setup
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create semi-transparent overlay
        overlay = QWidget(self)
        overlay.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.85); }")
        overlay.setGeometry(self.geometry())

        # Create content container
        content = QWidget(overlay)
        content.setFixedSize(480, 900)
        content.setStyleSheet("QWidget { background-color: white; border-radius: 12px; }")

        # Center content in overlay
        content_x = (overlay.width() - content.width()) // 2
        content_y = (overlay.height() - content.height()) // 2
        content.move(content_x, content_y)

        # Set up content layout
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 24, 32, 32)
        content_layout.setSpacing(24)

        # Create header
        header_layout = self.setup_header()
        content_layout.addLayout(header_layout)

        # Create form fields
        self.setup_form_fields(content_layout)

        # Create confirm button
        confirm_btn = self.setup_confirm_button()
        content_layout.addWidget(confirm_btn)

        # Add overlay to main layout
        main_layout.addWidget(overlay)

        # Initialize button state
        self.update_confirm_button()

    def setup_header(self):
        """Set up the header section with title and close button."""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        header_layout.setAlignment(Qt.AlignVCenter)

        # Create title
        title = QLabel("Add Peminjaman Record")
        title.setStyleSheet("""
            QLabel {
                color: #111827;
                font-family: 'Poly', sans-serif;
                font-size: 20px;
                font-weight: bold;
                margin: 0;
                padding: 0;
            }
        """)

        # Create close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6B7280;
                border: none;
                font-size: 24px;
                font-weight: bold;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                color: #111827;
            }
        """)
        close_btn.clicked.connect(self.reject)

        # Assemble header layout
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)

        return header_layout

    def setup_form_fields(self, parent_layout):
        """Set up the form fields for adding Peminjaman records."""
        placeholders = {
            'Nama': 'Customer name will be auto-filled',
            'NIK': 'Select NIK',
            'NomorPlat': 'Select Nomor Plat',
            'Kontak': 'Contact will be auto-filled',
            'TanggalPeminjaman': None,
            'TenggatPengembalian': None,
            'TenggatPembayaran': None,
            'BesarPembayaran': 'Enter payment amount'
        }

        fields = ['Nama', 'NIK', 'NomorPlat', 'Kontak', 'TanggalPeminjaman', 'TenggatPengembalian', 'TenggatPembayaran', 'BesarPembayaran']
        self.inputs = {}
        self.pelanggan_mapping = {}

        for field in fields:
            field_container = QWidget()
            field_layout = QVBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(4)

            label = QLabel(field)
            label.setStyleSheet("""
                QLabel {
                    color: #374151;
                    font-family: 'Poly', sans-serif;
                    font-size: 16px;
                    font-weight: 500;
                }
            """)
            field_layout.addWidget(label)

            if field in ['TanggalPeminjaman', 'TenggatPengembalian', 'TenggatPembayaran']:
                input_field = QDateEdit()
                input_field.setCalendarPopup(True)
                input_field.setDate(QDateEdit.date(input_field))
            elif field == 'NIK':
                input_field = QComboBox()
                pelanggan_data = self.controller.get_available_pelanggan()
                for nik, nama, kontak in pelanggan_data:
                    self.pelanggan_mapping[nik] = {'Nama': nama, 'Kontak': kontak}  # Store both Nama and Kontak
                    input_field.addItem(nik)
                input_field.currentIndexChanged.connect(self.update_nama_and_kontak_fields)  # Connect signal
            elif field == 'NomorPlat':
                input_field = QComboBox()
                mobil_data = self.controller.get_available_mobil()
                for nomor_plat, model in mobil_data:
                    input_field.addItem(nomor_plat)
                input_field.currentIndexChanged.connect(self.validate_nomor_plat_field)  # Connect signal
            else:
                input_field = QLineEdit()
                input_field.setPlaceholderText(placeholders[field])
                if field in ['Nama', 'Kontak']:
                    input_field.setReadOnly(True)  # Make the Nama and Kontak fields read-only
                elif field == 'BesarPembayaran':
                    input_field.textChanged.connect(self.validate_besar_pembayaran_inline)

            input_field.setFixedHeight(44)
            field_layout.addWidget(input_field)
            self.inputs[field] = input_field
            parent_layout.addWidget(field_container)
    
    def validate_nomor_plat_field(self):
        """Validate the NomorPlat field."""
        self.validation_states['NomorPlat'] = bool(self.inputs['NomorPlat'].currentText())
        self.update_confirm_button()


    def update_nama_and_kontak_fields(self):
        """Update the Nama and Kontak fields based on the selected NIK."""
        nik = self.inputs['NIK'].currentText()
        if nik in self.pelanggan_mapping:
            self.inputs['Nama'].setText(self.pelanggan_mapping[nik]['Nama'])
            self.inputs['Kontak'].setText(self.pelanggan_mapping[nik]['Kontak'])
            self.validation_states['NIK'] = True
            self.validation_states['Nama'] = True
            self.validation_states['Kontak'] = True
        else:
            self.inputs['Nama'].setText("")
            self.inputs['Kontak'].setText("")
            self.validation_states['NIK'] = False
            self.validation_states['Nama'] = False
            self.validation_states['Kontak'] = False
        self.update_confirm_button()

    def validate_besar_pembayaran_inline(self, text):
        """Validate BesarPembayaran field inline when the text changes."""
        try:
            value = int(text)
            self.validation_states['BesarPembayaran'] = value > 0
        except ValueError:
            self.validation_states['BesarPembayaran'] = False
        self.update_confirm_button()

    def update_confirm_button(self):
        """Enable or disable the Confirm button based on the validation states of all inputs."""
        is_valid = all(self.validation_states.values())
        self.confirm_button.setEnabled(is_valid)

    def setup_confirm_button(self):
        """Create and set up the confirm button."""
        confirm_btn = QPushButton("Add Record")
        confirm_btn.setFixedSize(376, 44)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4B5563;
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'Poly', sans-serif;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #374151;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
                cursor: not-allowed;
            }
        """)
        confirm_btn.clicked.connect(self.validate_and_accept)
        self.confirm_button = confirm_btn
        return confirm_btn

    def validate_and_accept(self):
        """Perform final validation and accept dialog if valid."""
        try:
            # Extract and validate data
            data = {
                'Nama': self.inputs['Nama'].text(),
                'NIK': self.inputs['NIK'].currentText(),
                'Nomor Plat': self.inputs['NomorPlat'].currentText(),
                'Kontak': self.inputs['Kontak'].text(),
                'Tanggal Peminjaman': self.inputs['TanggalPeminjaman'].date().toString("yyyy-MM-dd"),
                'Tenggat Pengembalian': self.inputs['TenggatPengembalian'].date().toString("yyyy-MM-dd"),
                'Tenggat Pembayaran': self.inputs['TenggatPembayaran'].date().toString("yyyy-MM-dd"),
                'Besar Pembayaran': int(self.inputs['BesarPembayaran'].text())
            }

            if not all(data.values()):
                raise ValueError("All fields must be filled.")
            
            # Pass validated data to the parent class
            self.accept()

        except ValueError as ve:
            QMessageBox.critical(self, "Input Error", str(ve))

    def get_data(self):
        """Retrieve the form data as a dictionary."""
        return {
            'Nama': self.inputs['Nama'].text(),
            'NIK': self.inputs['NIK'].currentText(),
            'NomorPlat': self.inputs['NomorPlat'].currentText(),
            'Kontak': self.inputs['Kontak'].text(),
            'TanggalPeminjaman': self.inputs['TanggalPeminjaman'].date().toString("yyyy-MM-dd"),
            'TenggatPengembalian': self.inputs['TenggatPengembalian'].date().toString("yyyy-MM-dd"),
            'TenggatPembayaran': self.inputs['TenggatPembayaran'].date().toString("yyyy-MM-dd"),
            'BesarPembayaran': int(self.inputs['BesarPembayaran'].text()),
            'StatusPengembalian': 1 if self.inputs['StatusPengembalian'].isChecked() else 0,
            'StatusPembayaran': 1 if self.inputs['StatusPembayaran'].isChecked() else 0
        }

class PeminjamanUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_window_geometry()
        
        self.db_path = Path(__file__).parent.parent / "Database/CarGoOwner.db"
        self.schema_path = Path(__file__).parent.parent / "schema.sql"
        self.controller = PeminjamanController()
        self.current_page = 1
        self.items_per_page = 20
        self.pagination_buttons = []  
        self.first_button = None
        self.prev_button = None
        self.next_button = None
        self.last_button = None
        
        # self.init_database()
        
        self.controller.init_database()

        self.setup_main_layout()
        
        self.load_data()

    def setup_window_geometry(self):
        """Set up the window geometry based on screen dimensions."""
        # Get screen dimensions
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        
        self.available_width = screen.width() - (screen.width() * 0.25) 
        
        self.screen_width = screen.width()
        self.screen_height = screen.height()

    def setup_main_layout(self):
        """Set up the main layout with proper spacing and margins."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self.setup_table()
        layout.addWidget(self.table)
        
        bottom_layout = self.setup_bottom_controls()
        layout.addLayout(bottom_layout)

    def handle_status_change(self, row, col, state):
        """Handle checkbox state changes for StatusPengembalian and StatusPembayaran."""
        try:
            # Determine the column name and corresponding date column
            if col == 9:  # StatusPengembalian
                status_column = "StatusPengembalian"
                date_column = "TanggalPengembalian"
            elif col == 10:  # StatusPembayaran
                status_column = "StatusPembayaran"
                date_column = "TanggalPembayaran"
            else:
                return

            # Get the primary key (e.g., NIK)
            nik_item = self.table.item(row, 1)
            if not nik_item:
                QMessageBox.warning(self, "Error", "Could not determine the record to update.")
                return
            nik = nik_item.text()

            # Determine the new status and date
            new_status = 1 if state == Qt.Checked else 0
            new_date = (
                datetime.datetime.now().strftime("%Y-%m-%d") if new_status == 1 else None
            )

            # Update the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE Peminjaman SET {status_column} = ?, {date_column} = ? WHERE NIK = ?",
                (new_status, new_date, nik),
            )
            conn.commit()

            # Update the UI
            date_item = QTableWidgetItem(new_date if new_date else "")
            date_item.setTextAlignment(Qt.AlignCenter)
            if col == 9:
                self.table.setItem(row, 5, date_item)  # TanggalPengembalian is column 5
            elif col == 10:
                self.table.setItem(row, 6, date_item)  # TanggalPembayaran is column 6

            print(f"Updated {status_column} to {new_status} and {date_column} to {new_date} for NIK {nik}.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()

    def setup_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Nama", "NIK", "Nomor Plat", "Kontak", 
            "Tanggal\nPeminjaman", "Tanggal\nPengembalian", 
            "Tanggal\nPembayaran", "Tenggat\nPengembalian", 
            "Besar\nPembayaran", "Status\nPengembalian", "Status\nPembayaran"
        ])
        
        # Define column percentages (total should be 100)
        column_percentages = {
            0: 12,   # Nama
            1: 12,   # NIK
            2: 10,   # Nomor Plat
            3: 10,   # Kontak
            4: 12,   # Tanggal Peminjaman
            5: 12,   # Tanggal Pengembalian
            6: 12,   # Tanggal Pembayaran
            7: 12,   # Tenggat Pengembalian
            8: 12,    # Besar Pembayaran
            9: 12,   # Status Pengembalian
            10: 12    # Status Pembayaran
        }
        
        # Calculate and set column widths based on available width
        for col, percentage in column_percentages.items():
            width = int(self.available_width * (percentage / 100))
            self.table.setColumnWidth(col, width)
        
        # Apply comprehensive table styling
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                font-family: 'Poly', sans-serif;
                text-align: center;
            }
            QHeaderView::section {
                background-color: white;
                border: none;
                font-family: 'Poly', sans-serif;
                color: #6B7280;
                font-size: 14px;
                text-align: center;
                height: 36px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F3F4F6;
                font-family: 'Poly', sans-serif;
                padding: 8px;
                min-height: 72px;
                text-align: center;
                                 
            }
        """)
        
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)


    def setup_bottom_controls(self):
        """Set up the bottom controls with proper spacing and alignment."""
        bottom_layout = QHBoxLayout()
        
        # Create Select/Deselect All button
        select_all_btn = QPushButton("Select/Deselect All")
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                color: #666666;
                font-family: 'Poly', sans-serif;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        select_all_btn.clicked.connect(self.toggle_select_all)
        
        # Set up pagination
        pagination_container = self.setup_pagination()
        
        # Create action buttons
        add_button = QPushButton("+")
        add_button.setFixedSize(56, 56)
        add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#10B981'};
                border-radius: 28px;
                color: white;
                font-size: 24px;
            }}
            QPushButton:hover {{
                background-color: {'#059669'};
            }}
        """)    
            
        add_button.clicked.connect(self.handle_add_peminjaman)
        
        # Assemble the bottom layout
        bottom_layout.addWidget(select_all_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(pagination_container)
        bottom_layout.addStretch()
        bottom_layout.addWidget(add_button)
        bottom_layout.addSpacing(10)
        
        return bottom_layout

    def setup_pagination(self):
        """Set up pagination with a fixed window of 5 pages plus First/Last buttons."""
        # Create container widget
        pagination_container = QWidget()
        pagination_layout = QHBoxLayout(pagination_container)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(8)
        
        # Calculate total pages
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM Peminjaman')
        total_records = cursor.fetchone()[0]
        self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
        conn.close()
        
        # Style for all pagination buttons
        button_style = """
            QPushButton {
                background: none;
                border: none;
                color: #374151;
                font-family: 'Poly', sans-serif;
                font-size: 14px;
                padding: 8px;
                min-width: 30px;
            }
            QPushButton:hover { color: #000000; }
            QPushButton:disabled { color: #9CA3AF; }
            QPushButton[current="true"] {
                font-weight: bold;
                color: #000000;
            }
        """
        
        # Clear existing buttons
        self.pagination_buttons = []
        
        # Create navigation buttons
        self.first_button = QPushButton("First")
        self.prev_button = QPushButton("←")
        self.next_button = QPushButton("→")
        self.last_button = QPushButton("Last")
        
        for btn in [self.first_button, self.prev_button, self.next_button, self.last_button]:
            btn.setStyleSheet(button_style)
        
        # Add First and Prev buttons
        pagination_layout.addWidget(self.first_button)
        pagination_layout.addWidget(self.prev_button)
        
        # Calculate the range of pages to display (sliding window of 5)
        def calculate_page_range():
            n = 5  # Number of page buttons to show
            if self.total_pages <= n:
                # If total pages is less than window size, show all pages
                start_page = 1
                end_page = self.total_pages
            else:
                # Calculate the start page based on current page
                start_page = max(1, min(self.current_page - n//2, self.total_pages - n + 1))
                end_page = start_page + n - 1
                
                # Adjust if we're near the end
                if end_page > self.total_pages:
                    end_page = self.total_pages
                    start_page = max(1, end_page - n + 1)
            
            return range(start_page, end_page + 1)
        
        # Add page buttons
        for page in calculate_page_range():
            btn = QPushButton(str(page))
            btn.setStyleSheet(button_style)
            if page == self.current_page:
                btn.setProperty("current", "true")
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            btn.setProperty("page_number", page)
            btn.clicked.connect(lambda checked, p=page: self.go_to_page(p))
            self.pagination_buttons.append(btn)
            pagination_layout.addWidget(btn)
        
        # Add Next and Last buttons
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addWidget(self.last_button)
        
        # Connect navigation button signals
        self.first_button.clicked.connect(lambda: self.go_to_page(1))
        self.prev_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        self.last_button.clicked.connect(lambda: self.go_to_page(self.total_pages))
        
        # Update button states
        self.update_pagination_buttons()
        
        return pagination_container

    def update_pagination_buttons(self):
        """Update the enabled state of all pagination buttons."""
        if all([self.first_button, self.prev_button, self.next_button, self.last_button]):
            # Disable First/Prev buttons if on first page
            self.first_button.setEnabled(self.current_page > 1)
            self.prev_button.setEnabled(self.current_page > 1)
            
            # Disable Next/Last buttons if on last page
            self.next_button.setEnabled(self.current_page < self.total_pages)
            self.last_button.setEnabled(self.current_page < self.total_pages)

    def go_to_page(self, page):
        """Navigate to a specific page number."""
        if 1 <= page <= self.total_pages and page != self.current_page:
            self.current_page = page
            self.load_data()
            # Recreate pagination with updated current page
            bottom_layout = self.findChild(QHBoxLayout)
            if bottom_layout:
                # Find and remove the old pagination container
                for i in range(bottom_layout.count()):
                    item = bottom_layout.itemAt(i)
                    if item and isinstance(item.widget(), QWidget):
                        if isinstance(item.widget().layout(), QHBoxLayout):
                            item.widget().deleteLater()
                            break
                
                # Create and add new pagination container
                new_pagination = self.setup_pagination()
                # Add it at the same position (index 2)
                bottom_layout.insertWidget(2, new_pagination)

    def previous_page(self):
        """Navigate to the previous page."""
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)

    def next_page(self):
        """Navigate to the next page."""
        if self.current_page < self.total_pages:
            self.go_to_page(self.current_page + 1)

    def update_status_in_db(self, row, col, state):
        """Update the StatusPengembalian or StatusPembayaran column in the database."""
        try:
            # Determine the column name based on `col`
            column_name = "StatusPengembalian" if col == 9 else "StatusPembayaran"

            # Get the primary key or unique identifier (e.g., NIK or row ID)
            nik_item = self.table.item(row, 1)  # Assuming column 1 contains the NIK
            if not nik_item:
                QMessageBox.warning(self, "Error", "Could not determine the record to update.")
                return
            nik = nik_item.text()

            # Update the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"UPDATE Peminjaman SET {column_name} = ? WHERE NIK = ?", (state, nik))
            conn.commit()

            # Log success
            print(f"Updated {column_name} for NIK {nik} to {state}.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while updating the database: {e}")
        finally:
            if conn:
                conn.close()

    def load_data(self):
        # Fetch data from controller
        offset = (self.current_page - 1) * self.items_per_page
        records = self.controller.fetch_peminjaman(offset=offset, limit=self.items_per_page)
        
        if not records:
            print("No records found.")
            self.table.setRowCount(0)  # Clear table if no data
            return


        # Populate the table
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            for col, value in enumerate(record):
                if col == 9 or col == 10:
                    checkbox = QCheckBox()
                    checkbox.setChecked(bool(value))  # Convert 0/1 to False/True
                    checkbox.stateChanged.connect(lambda state, r=row, c=col: self.handle_status_change(r, c, state))
                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(checkbox)

                    self.table.setCellWidget(row, col, container)
                
                else:
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)

    def create_status_cell(self, row, col, is_pinjam):
        """Create a styled status cell indicating whether a customer has borrowed items."""
        status_text = "Pinjam" if is_pinjam else "Tidak Pinjam"
        status_btn = QPushButton(status_text)
        status_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#D1FAE5' if is_pinjam else '#FEE2E2'};
                color: {'#10B981' if is_pinjam else '#EF4444'};
                border: 1px solid {'#10B981' if is_pinjam else '#EF4444'};
                border-radius: 10px;
                padding-right: 12px;
                padding-left: 12px;
                min-height: 30px;
                min-width: 100px;
                font-family: 'Poly', sans-serif;
                font-weight: 500;
                font-size: 14px;
                text-align: center;
            }}
        """)
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(status_btn, alignment=Qt.AlignCenter)
        self.table.setCellWidget(row, col, container)

    def create_action_cell(self, row):
        """Create a styled action cell with an edit button for each customer row."""
        action_btn = QPushButton("✎")
        action_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #6B7280;
                font-size: 16px;
                font-family: 'Poly', sans-serif;
            }
            QPushButton:hover {
                color: #374151;
            }
        """)
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(action_btn, alignment=Qt.AlignCenter)
        self.table.setCellWidget(row, 7, container)
        
        # Connect the button to edit handler
        action_btn.clicked.connect(lambda: self.handle_edit(row))

    def handle_edit(self, row):
        """Handle the edit action when a customer's edit button is clicked."""
        # Get the NIK of the selected customer
        nik_item = self.table.item(row, 1)
        if nik_item:
            nik = nik_item.text()
            print(f"Editing customer with NIK: {nik}")
            # TODO: Implement edit dialog functionality

    def toggle_select_all(self, checked=None):
        """Toggle selection state of all checkboxes in the table."""
        # If checked is None, determine state based on first checkbox
        if checked is None:
            first_checkbox = self.get_checkbox(0)
            if first_checkbox:
                checked = not first_checkbox.isChecked()
        
        # Update all checkboxes
        for row in range(self.table.rowCount()):
            checkbox = self.get_checkbox(row)
            if checkbox:
                checkbox.setChecked(checked)

    def get_checkbox(self, row):
        """Helper method to get checkbox widget from a specific row."""
        checkbox_container = self.table.cellWidget(row, 0)
        if checkbox_container:
            return checkbox_container.layout().itemAt(0).widget()
        return None

    def get_selected_rows(self):
        """Get a list of indices for all selected rows."""
        selected_rows = []
        for row in range(self.table.rowCount()):
            checkbox = self.get_checkbox(row)
            if checkbox and checkbox.isChecked():
                selected_rows.append(row)
        return selected_rows

    def handle_add_peminjaman(self):
        """Handle the addition of a new peminjaman record."""
        dialog = AddPeminjamanDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            print(f"Adding new peminjaman record: {data}")

            if any(value is None or value == "" for value in data.values()):
                missing_fields = [key for key, value in data.items() if value is None or value == ""]
                QMessageBox.warning(self, "Validation Error", f"The following fields are required and missing: {', '.join(missing_fields)}")
                print("Validation failed. Missing fields:", missing_fields)
                return


            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO Peminjaman (
                        Nama, NIK, NomorPlat, Kontak, 
                        TanggalPeminjaman, TenggatPengembalian, 
                        TenggatPembayaran, BesarPembayaran, 
                        StatusPengembalian, StatusPembayaran
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['Nama'],
                    data['NIK'],
                    data['NomorPlat'],
                    data['Kontak'],
                    data['TanggalPeminjaman'],
                    data['TenggatPengembalian'],
                    data['TenggatPembayaran'],
                    data['BesarPembayaran'],
                    data['StatusPengembalian'],
                    data['StatusPembayaran']
                ))

                conn.commit()
                self.load_data()
                QMessageBox.information(self, "Success", "Peminjaman added successfully!")

            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, "Error", f"Database Integrity Error: {e}")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
            finally:
                if conn:
                    conn.close()
