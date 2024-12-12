import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                           QDesktopWidget)
from PyQt5.QtCore import Qt
import sqlite3

class StatusPengembalian(QWidget):
    def __init__(self, schema_path, parent=None):
        """Initialize the Pelanggan (Customer) UI with complete styling and functionality."""
        super().__init__(parent)
        
        # Initialize screen dimensions and layout calculations
        self.setup_window_geometry()
        
        # Store important paths for database access
        self.schema_path = schema_path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(schema_path)))
        self.db_path = os.path.join(self.base_dir, "src/CarGoOwnerPeminjaman.db")
        
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
        self.available_width = screen.width() - (screen.width() * 0.22) 
        
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

        self.message_error = QLabel("Tidak ada notifikasi", self)
        self.message_error.setAlignment(Qt.AlignCenter)
        self.message_error.setStyleSheet("font-size: 18px; color: #6B7280;")
        layout.addWidget(self.message_error)
        self.message_error.hide()


    def setup_table(self):
        """Set up the table with calculated column widths based on screen size."""
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            #"", "NIK", "Nama", "Kontak", "Alamat", "Credit Point", "Status", "Aksi"
            "ID", "NIK", "Nama", "Kontak", "Nomor Plat", "Tanggal Peminjaman", "Tanggal Pengembalian", "Status Pengembalian"
        ])
        
        # Define column percentages (total should be 100)
        column_percentages = {
            0: 1,     # ID
            1: 15,    # NIK
            2: 15,    # Nama
            3: 12,    # Kontak
            4: 14,    # NomorPlat
            5: 14,    # TanggalPeminjaman
            6: 14,    # TanggalPengembalian
            7: 12     # StatusPengembalian
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
                text-align: left;
            }
            QHeaderView::section {
                background-color: white;
                padding: 16px;
                border: none;
                font-family: 'Poly', sans-serif;
                color: #6B7280;
                font-size: 14px;
                text-align: left;
                height: 24px;
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
        
        # Set up pagination
        pagination_container = self.setup_pagination()
        
        # Assemble the bottom layout
        bottom_layout.addStretch()
        bottom_layout.addWidget(pagination_container)
        bottom_layout.addStretch()
        
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
        """Initialize the database and create tables with sample customer data."""
        try:
            # Establish database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create the Pelanggan table with proper column order
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Peminjaman (
                    ID INTEGER PRIMARY KEY,
                    NomorPlat TEXT,
                    NIK TEXT,
                    Nama TEXT,
                    Kontak TEXT,
                    TanggalPeminjaman DATE,
                    TanggalPengembalian DATE,
                    TanggalPembayaran DATE,
                    TenggatPengembalian DATE,
                    TenggatPembayaran DATE,
                    BesarPembayaran INTEGER,
                    StatusPengembalian INTEGER,
                    StatusPembayaran INTEGER
                )
            ''')
            
            # Check if table is empty and needs sample data
            cursor.execute('SELECT COUNT(*) FROM Peminjaman')
            if cursor.fetchone()[0] == 0:
                # Prepare sample data with 60 varied entries
                sample_data = [
                    ('B 5001 KGG', '3201001991010001', 'Yu Ji-min', '081234567891', '2024-12-01', '2024-12-05', '2024-12-06', '2024-12-05', '2024-12-06', 550000, 1, 1),
                    ('B 5002 SGG', '3202002991020002', 'Aeri Uchinaga', '082345678902', '2024-12-02', None, None, '2024-12-10', '2024-12-12', 750000, 0, 0),
                    ('B 5003 NIN', '3203003991030003', 'Kim Min-Jeong', '083456789013', '2024-12-03', '2024-12-07', '2024-12-08', '2024-12-07', '2024-12-09', 600000, 1, 1),
                    ('B 5004 NYN', '3204004991040004', 'Níng Yìzhuó', '084567890124', '2024-12-04', None, None, '2024-12-11', '2024-12-13', 800000, 0, 0),
                    ('B 5005 HKL', '3205005991050005', 'Julie Han', '085678901235', '2024-12-05', '2024-12-09', '2024-12-10', '2024-12-09', '2024-12-11', 650000, 1, 1),
                    ('B 5006 JKL', '3206006991060006', 'Anatchaya Suputtipong', '086789012346', '2024-12-06', None, None, '2024-12-13', '2024-12-15', 700000, 0, 0),
                    ('B 5007 SKL', '3207007991070007', 'Shim Hyewon', '087890123457', '2024-12-07', '2024-12-11', '2024-12-12', '2024-12-11', '2024-12-13', 620000, 1, 1),
                    ('B 5008 PKL', '3208008991080008', 'Won Haneul', '088901234568', '2024-12-08', None, None, '2024-12-15', '2024-12-17', 780000, 0, 0),
                    ('B 5009 NTW', '3209009991090009', 'Park Jihyo', '089012345679', '2024-12-09', '2024-12-13', '2024-12-14', '2024-12-13', '2024-12-15', 680000, 1, 1),
                    ('B 5010 JTW', '3210010991100010', 'Im Na Yeon', '081123456780', '2024-12-10', None, None, '2024-12-17', '2024-12-19', 720000, 0, 0),
                    ('B 5011 MTW', '3211011991110011', 'Yoo Jeong Yeon', '082234567891', '2024-12-11', '2024-12-15', '2024-12-16', '2024-12-15', '2024-12-17', 590000, 1, 1),
                    ('B 5012 STW', '3212012991120012', 'Hirai Momo', '083345678902', '2024-12-12', None, None, '2024-12-19', '2024-12-21', 810000, 0, 0),
                    ('B 5013 DTW', '3213013991130013', 'Minatozaki Sana', '084456789013', '2024-12-13', '2024-12-17', '2024-12-18', '2024-12-17', '2024-12-19', 640000, 1, 1),
                    ('B 5014 CTW', '3214014991140014', 'Myoui Mina', '085567890124', '2024-12-14', None, None, '2024-12-21', '2024-12-23', 690000, 0, 0),
                    ('B 5015 MTW', '3215015991150015', 'Kim Da Hyun', '086678901235', '2024-12-15', '2024-12-19', '2024-12-20', '2024-12-19', '2024-12-21', 760000, 1, 1),
                    ('B 5016 TTW', '3216016991160016', 'Son Chae Young', '087789012346', '2024-12-16', None, None, '2024-12-23', '2024-12-25', 790000, 0, 0),
                    ('B 5017 HTW', '3217017991170017', 'Chou Tzuyu', '088890123457', '2024-12-17', '2024-12-21', '2024-12-22', '2024-12-21', '2024-12-23', 670000, 1, 1),
                    ('B 5018 RJK', '3218018991180018', 'Kim Minji', '089901234568', '2024-12-18', '2024-12-22', '2024-12-23', '2024-12-22', '2024-12-24', 610000, 1, 1),
                    ('B 5019 BJK', '3219019991190019', 'Hanni Pham', '081012345679', '2024-12-19', None, None, '2024-12-26', '2024-12-28', 730000, 0, 0),
                    ('B 5020 DJK', '3220020991200020', 'Danielle Marsh', '082123456780', '2024-12-20', '2024-12-24', '2024-12-25', '2024-12-24', '2024-12-26', 660000, 1, 1),
                    ('B 5021 FJK', '3221021991210021', 'Kang Haerin', '083234567891', '2024-12-21', None, None, '2024-12-28', '2024-12-30', 770000, 0, 0),
                    ('B 5022 GJK', '3222022991220022', 'Lee Hyein', '084345678902', '2024-12-22', '2024-12-26', '2024-12-27', '2024-12-26', '2024-12-28', 630000, 1, 1),
                    ('B 5023 HJK', '3223023991230023', 'Hu Tao', '085456789013', '2024-12-23', None, None, '2024-12-30', '2024-01-01', 800000, 0, 0),
                    ('B 5024 IJK', '3224024991240024', 'Ucok Gallagher', '086567890124', '2024-12-24', '2024-12-28', '2024-12-29', '2024-12-28', '2024-12-30', 690000, 1, 1),
                    ('B 5025 JJK', '3225025991250025', 'Yayat Sigam', '087678901235', '2024-12-25', None, None, '2024-01-01', '2024-01-03', 740000, 0, 0),
                    ('B 5026 KJK', '3226026991260026', 'Rzi Rach', '088789012346', '2024-12-26', '2024-12-30', '2024-12-31', '2024-12-30', '2024-01-01', 620000, 1, 1),
                    ('B 5027 LJK', '3227027991270027', 'Dittt PWN', '089890123457', '2024-12-27', None, None, '2024-01-03', '2024-01-05', 710000, 0, 0),
                    ('B 5028 MJK', '3228028991280028', 'W1ntr', '081901234568', '2024-12-28', '2024-01-01', '2024-01-02', '2024-01-01', '2024-01-03', 650000, 1, 1),
                    ('B 5029 NJK', '3229029991290029', 'Freya Jayawardhana', '082012345679', '2024-12-29', None, None, '2024-01-06', '2024-01-08', 790000, 0, 0),
                    ('B 5030 OJK', '3230030991300030', 'Rizialfa', '083123456780', '2024-12-30', '2024-01-03', '2024-01-04', '2024-01-03', '2024-01-05', 680000, 1, 1)
                ]
                
                # Insert all sample data
                cursor.executemany('''
                    INSERT INTO Peminjaman (NomorPlat, NIK, Nama, Kontak, TanggalPeminjaman, TanggalPengembalian, TanggalPembayaran, TenggatPengembalian, TenggatPembayaran, BesarPembayaran, StatusPengembalian, StatusPembayaran)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_data)
                
            # Commit changes and ensure they're saved
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            
        finally:
            # Ensure connection is closed even if an error occurs
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
                SELECT ID, NIK, Nama, Kontak, NomorPlat, TanggalPeminjaman, TanggalPengembalian, StatusPengembalian FROM Peminjaman 
                LIMIT {self.items_per_page} 
                OFFSET {offset}
            ''')
            data = cursor.fetchall()

            if not data:
                # No data to display
                self.table.setColumnCount(0)
                self.table.setRowCount(0)

                # Clear pagination buttons
                for btn in self.pagination_buttons:
                    btn.deleteLater()
                self.pagination_buttons.clear()

                # Update button states
                self.update_pagination_buttons()

                self.message_error.show()
                return
            
            # Set up table rows
            self.message_error.hide()
            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                # Add data cells
                for col, value in enumerate(record):
                    if col == 7:  # Status column
                        self.create_status_cell(row, col, value == 1)
                    else:
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(row, col, item)
                
                # Set row height
                self.table.setRowHeight(row, 115)
            
        except sqlite3.Error as e:
            print(f"Error loading data: {e}")
            
        finally:
            if conn:
                conn.close()

    def create_status_cell(self, row, col, is_kembali):
        """Create a styled status cell indicating whether a customer has borrowed items."""
        status_text = "Sudah" if is_kembali else "Belum"
        status_btn = QPushButton(status_text)
        status_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#D1FAE5' if is_kembali else '#FEE2E2'};
                color: {'#10B981' if is_kembali else '#EF4444'};
                border: 1px solid {'#10B981' if is_kembali else '#EF4444'};
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