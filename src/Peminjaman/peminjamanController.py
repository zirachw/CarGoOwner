import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                           QFrame, QSizePolicy, QCheckBox, QToolButton, QDesktopWidget)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QIcon
import sqlite3

class PeminjamanController(QWidget):
    def __init__(self, schema_path, parent=None):
        super().__init__(parent)
        
        # Initialize screen dimensions and layout calculations
        self.setup_window_geometry()
        
        # Store important paths for database access
        self.schema_path = schema_path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(schema_path)))
        self.db_path = os.path.join(self.base_dir, "src/CarGoOwnerPelanggan.db")
        
        # Initialize pagination variables
        self.current_page = 1
        self.items_per_page = 10
        self.pagination_buttons = []  # Store pagination buttons
        
        # Initialize navigation button references
        self.first_button = None
        self.prev_button = None
        self.next_button = None
        self.last_button = None
        
        # Initialize database before setting up UI
        self.init_database()
        
        # Create main layout with proper spacing
        self.setup_main_layout()
        
        # Load the initial data
        self.load_data()

    def setup_window_geometry(self):
        """Set up the window geometry based on screen dimensions."""
        # Get screen dimensions
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        
        # Calculate available width (total width minus 25% for sidebar)
        self.available_width = screen.width() - (screen.width() * 0.25) 
        
        # Store dimensions for later use
        self.screen_width = screen.width()
        self.screen_height = screen.height()

    def setup_main_layout(self):
        """Set up the main layout with proper spacing and margins."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Initialize and setup the table
        self.setup_table()
        layout.addWidget(self.table)
        
        # Setup bottom controls (pagination, buttons)
        bottom_layout = self.setup_bottom_controls()
        layout.addLayout(bottom_layout)

    def setup_table(self):
        """Set up the table with adjusted column widths based on screen size."""
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "", "Nama", "NIK", "Nomor Plat", "Kontak", 
            "Tanggal Peminjaman", "Tanggal Pengembalian", 
            "Tanggal Pembayaran", "Tenggat Pengembalian", 
            "Besar Pembayaran", "Status Pengembalian", "Status Pembayaran"
        ])
        
        # Define column percentages (total should be 100)
        column_percentages = {
            0: 5,    # ID
            1: 12,   # Nama
            2: 12,   # NIK
            3: 10,   # Nomor Plat
            4: 10,   # Kontak
            5: 12,   # Tanggal Peminjaman
            6: 12,   # Tanggal Pengembalian
            7: 12,   # Tanggal Pembayaran
            8: 12,   # Tenggat Pengembalian
            9: 8,    # Besar Pembayaran
            10: 8,   # Status Pengembalian
            11: 8    # Status Pembayaran
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
            }
            QHeaderView::section {
                background-color: white;
                padding: 16px;
                border: none;
                font-family: 'Poly', sans-serif;
                color: #6B7280;
                font-size: 14px;
                text-align: left;
                height: 36px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #F3F4F6;
                font-family: 'Poly', sans-serif;
                padding: 8px;
                min-height: 72px;
            }
        """)
        
        # Configure additional table properties
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
        delete_button = QPushButton("×")
        
        for btn in (add_button, delete_button):
            btn.setFixedSize(56, 56)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {('#10B981' if btn == add_button else '#EF4444')};
                    border-radius: 28px;
                    color: white;
                    font-size: 24px;
                }}
                QPushButton:hover {{
                    background-color: {('#059669' if btn == add_button else '#DC2626')};
                }}
            """)
        
        # Connect delete button to handler
        delete_button.clicked.connect(self.handle_delete_selected)
        
        # Assemble the bottom layout
        bottom_layout.addWidget(select_all_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(pagination_container)
        bottom_layout.addStretch()
        bottom_layout.addWidget(add_button)
        bottom_layout.addSpacing(10)
        bottom_layout.addWidget(delete_button)
        
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

   
    def init_database(self):
        """Initialize the database and create tables with sample data."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")  # Ensure foreign key support is enabled
            cursor = conn.cursor()

            # Create the Mobil table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Mobil (
                    NomorPlat TEXT PRIMARY KEY,
                    Merk TEXT NOT NULL,
                    Model TEXT NOT NULL,
                    Tahun INTEGER NOT NULL
                )
            ''')

            # Create the Pelanggan table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Pelanggan (
                    NIK TEXT PRIMARY KEY,
                    Nama TEXT NOT NULL,
                    Alamat TEXT NOT NULL,
                    Kontak TEXT NOT NULL
                )
            ''')

            # Create the Peminjaman table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Peminjaman (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Nama TEXT NOT NULL,
                    NIK TEXT NOT NULL,

                    NomorPlat TEXT NOT NULL,
                    Kontak TEXT NOT NULL,
                    TanggalPeminjaman DATETIME NOT NULL,
                    TanggalPengembalian DATETIME,
                    TanggalPembayaran DATETIME,
                    TenggatPengembalian DATETIME NOT NULL,
                    TenggatPembayaran DATETIME NOT NULL,
                    BesarPembayaran INTEGER NOT NULL,
                    StatusPengembalian INTEGER DEFAULT 0 CHECK (StatusPengembalian IN (0, 1)),
                    StatusPembayaran INTEGER DEFAULT 0 CHECK (StatusPembayaran IN (0, 1)),
                    FOREIGN KEY (NomorPlat) REFERENCES Mobil(NomorPlat),
                    FOREIGN KEY (NIK) REFERENCES Pelanggan(NIK)
                )
            ''')

            # Insert sample data for Mobil if the table is empty
            cursor.execute('SELECT COUNT(*) FROM Mobil')
            if cursor.fetchone()[0] == 0:
                sample_mobil = [
                    ('AB1234CD', 'Toyota', 'Avanza', 2020),
                    ('B5678EF', 'Honda', 'Jazz', 2021),
                    ('C9101GH', 'Suzuki', 'Ertiga', 2019),
                    ('D2345IJ', 'Nissan', 'Livina', 2020),
                    ('E6789KL', 'Mitsubishi', 'Xpander', 2021),
                ]
                cursor.executemany('''
                    INSERT INTO Mobil (NomorPlat, Merk, Model, Tahun)
                    VALUES (?, ?, ?, ?)
                ''', sample_mobil)

            # Insert sample data for Pelanggan if the table is empty
            cursor.execute('SELECT COUNT(*) FROM Pelanggan')
            if cursor.fetchone()[0] == 0:
                sample_pelanggan = [
                    ('3201234567890123', 'John Doe', 'Jl. Sudirman No. 1', '081234567890'),
                    ('3209876543210987', 'Jane Smith', 'Jl. Thamrin No. 2', '082345678901'),
                    ('3205678901234567', 'Michael Johnson', 'Jl. Merdeka No. 3', '083456789012'),
                    ('3203456789012345', 'Emily Davis', 'Jl. Gajah Mada No. 4', '084567890123'),
                    ('3201230987654321', 'Robert Brown', 'Jl. Diponegoro No. 5', '085678901234'),
                ]
                cursor.executemany('''
                    INSERT INTO Pelanggan (NIK, Nama, Alamat, Kontak)
                    VALUES (?, ?, ?, ?)
                ''', sample_pelanggan)

            # Insert sample data for Peminjaman if the table is empty
            cursor.execute('SELECT COUNT(*) FROM Peminjaman')
            if cursor.fetchone()[0] == 0:
                sample_peminjaman = [
                    ('AB1234CD', '3201234567890123', 'John Doe', '081234567890',
                    '2024-12-01 10:00:00', '2024-12-07 15:00:00', '2024-12-07 17:00:00',
                    '2024-12-07 15:00:00', '2024-12-07 17:00:00', 500000, 1, 1),
                    ('B5678EF', '3209876543210987', 'Jane Smith', '082345678901',
                    '2024-12-02 12:00:00', None, None, '2024-12-08 12:00:00', '2024-12-08 15:00:00',
                    600000, 0, 0),
                    ('C9101GH', '3205678901234567', 'Michael Johnson', '083456789012',
                    '2024-11-28 09:00:00', '2024-12-05 14:00:00', '2024-12-05 14:30:00',
                    '2024-12-05 14:00:00', '2024-12-05 14:30:00', 450000, 1, 1),
                    ('D2345IJ', '3203456789012345', 'Emily Davis', '084567890123',
                    '2024-11-30 11:30:00', None, None, '2024-12-06 11:30:00', '2024-12-06 14:00:00',
                    550000, 0, 0),
                    ('E6789KL', '3201230987654321', 'Robert Brown', '085678901234',
                    '2024-12-03 14:00:00', None, None, '2024-12-09 14:00:00', '2024-12-09 16:00:00',
                    700000, 0, 0),
                ]
                cursor.executemany('''
                    INSERT INTO Peminjaman (NomorPlat, NIK, Nama, Kontak, TanggalPeminjaman, 
                                            TanggalPengembalian, TanggalPembayaran, 
                                            TenggatPengembalian, TenggatPembayaran, 
                                            BesarPembayaran, StatusPengembalian, StatusPembayaran)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_peminjaman)

            # Commit changes
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                conn.close()


    def load_data(self):
        """Load and display data from the database with pagination."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate offset based on current page
            offset = (self.current_page - 1) * self.items_per_page
            cursor.execute(f'''
                SELECT * FROM Peminjaman 
            ''')
            data = cursor.fetchall()
            
            # Set up table rows
            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                # Add checkbox
                checkbox = QCheckBox()
                checkbox_container = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_container)
                checkbox_layout.setContentsMargins(16, 16, 16, 16)
                checkbox_layout.addWidget(checkbox, alignment=Qt.AlignCenter)
                self.table.setCellWidget(row, 0, checkbox_container)
                
                # Add data cells
                for col, value in enumerate(record):
                    if col == 5:  # Status column
                        self.create_status_cell(row, col + 1, value == 1)
                    else:
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(row, col + 1, item)
                
                # Add action button
                self.create_action_cell(row)
                
                # Set row height
                self.table.setRowHeight(row, 72)
            
        except sqlite3.Error as e:
            print(f"Error loading data: {e}")
            
        finally:
            if conn:
                conn.close()

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

    def handle_delete_selected(self):
        """Delete all selected customers from the database."""
        selected_rows = self.get_selected_rows()
        if not selected_rows:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for row in selected_rows:
                nik_item = self.table.item(row, 1)
                if nik_item:
                    nik = nik_item.text()
                    cursor.execute('DELETE FROM Pelanggan WHERE NIK = ?', (nik,))
            
            conn.commit()
            
            # Recalculate total pages and adjust current page if needed
            cursor.execute('SELECT COUNT(*) FROM Peminjaman')
            total_records = cursor.fetchone()[0]
            new_total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
            
            # Adjust current page if it's now beyond the total pages
            if self.current_page > new_total_pages:
                self.current_page = max(1, new_total_pages)
            
            # Reload data and update pagination
            self.load_data()
            
            # Recreate pagination controls
            bottom_layout = self.findChild(QHBoxLayout)
            if bottom_layout:
                # Find and remove old pagination container
                for i in range(bottom_layout.count()):
                    item = bottom_layout.itemAt(i)
                    if item and isinstance(item.widget(), QWidget):
                        if isinstance(item.widget().layout(), QHBoxLayout):
                            item.widget().deleteLater()
                            break
                
                # Create and add new pagination container
                new_pagination = self.setup_pagination()
                bottom_layout.insertWidget(2, new_pagination)
            
        except sqlite3.Error as e:
            print(f"Error deleting records: {e}")
            
        finally:
            if conn:
                conn.close()        