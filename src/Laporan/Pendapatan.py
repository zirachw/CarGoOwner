import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                           QFrame, QSizePolicy, QCheckBox, QToolButton, QDesktopWidget, QComboBox)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QIcon
import sqlite3, locale
from pathlib import Path

class PendapatanUI(QWidget):
    def __init__(self, parent=None):
        """Initialize the Pelanggan (Customer) UI with complete styling and functionality."""
        super().__init__(parent)

        # Initialize screen dimensions and layout calculations
        self.ShowLaporanPendapatanUI()
        
        # Store important paths for database access
        self.db_path = Path(__file__).parent.parent / "Database/CarGoOwner.db"
        
        # Initialize pagination variables
        self.current_page = 1
        self.items_per_page = 10
        self.pagination_buttons = []  # Store pagination buttons
        
        # Initialize navigation button references
        self.first_button = None
        self.prev_button = None
        self.next_button = None
        self.last_button = None

        self.setup_main_layout()
        self.load_data()

    def ShowLaporanPendapatanUI(self):
        """Set up the window geometry based on screen dimensions."""
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
        
        # Calculate total pages
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM (SELECT ID, Nama, TanggalPeminjaman, TanggalPengembalian, TenggatPengembalian, BesarPembayaran FROM Peminjaman)')
        total_records = cursor.fetchone()[0]
        self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
        conn.close()

        # If no records, hide pagination and return empty container
        self.message_error = QLabel("Tidak ada Data", self)
        self.message_error.hide()
        if total_records == 0:
            self.message_error.setAlignment(Qt.AlignCenter)
            self.message_error.setStyleSheet("font-size: 42px; font-family: 'Poly', sans-serif; color: #6B7280;")
            layout.addWidget(self.message_error)
            return

        top_layout = self.setup_top_bar()
        layout.addLayout(top_layout)

        # Initialize and setup the table
        self.setup_table()
        layout.addWidget(self.table)
        
        # Setup bottom controls (pagination, buttons)
        bottom_layout = self.setup_bottom_controls()
        layout.addLayout(bottom_layout)

    def setup_table(self):
        """Set up the table with calculated column widths based on screen size."""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nama", "Tanggal Peminjaman", "Tanggal Pengembalian", "Tanggal Pembayaran", "Besar Pembayaran"
        ])
        
        column_percentages = {
            0: 5,     # Checkbox
            1: 20,    # NIK
            2: 20,    # Nama
            3: 20,    # Kontak
            4: 20,    # Alamat
            5: 15     # Credit Point
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

    def get_total_pembayaran(self):
        conn = sqlite3.connect(self.db_path)  # Ganti dengan nama database Anda
        cursor = conn.cursor()

        # Query untuk mengambil total jumlah
        cursor.execute("SELECT sum(BesarPembayaran) AS totalPembayaran FROM Peminjaman WHERE StatusPembayaran = 1")
        result = cursor.fetchone()  # Ambil hasil pertama (karena hanya ada satu baris)
        
        # Tutup koneksi setelah selesai
        conn.close()
        return result[0] 

    def setup_top_bar(self):
        top_bar = QHBoxLayout()

        locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

        total = self.get_total_pembayaran()
        if not total :
            total = 0

        formatted_number = locale.currency(total, grouping=True)
        label = QLabel(f"Total Pembayaran: {formatted_number}")

        label.setStyleSheet("""
            background-color: #D3D3D3;   /* Warna abu-abu */
            border-radius: 15px;         /* Sudut bundar */
            padding: 10px;               /* Ruang di dalam label */
            font-size: 14px;             /* Ukuran font */
            font-family: 'Poly', sans-serif;
            color: black;                /* Warna teks */
        """)

        self.periode_dropdown = QComboBox()
        self.periode_dropdown.setFont(QFont("Poly", 12))
        self.periode_dropdown.setStyleSheet("""
            QComboBox {
                padding: 8px;
                padding-left: 20px;
                border: 1px solid #D1D5DB;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
        """)
        self.periode_dropdown.addItem("All Periode")
        self.periode_dropdown.addItems(self.get_unique_month())
        self.periode_dropdown.currentIndexChanged.connect(self.apply_filters)

        top_bar.addWidget(self.periode_dropdown)
        top_bar.addSpacing(20)
        top_bar.addWidget(label)
        top_bar.addStretch()

        return top_bar

    def get_unique_month(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT strftime('%m' ,TanggalPembayaran) AS bulan FROM Peminjaman")
            months = cursor.fetchall()
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt','Nov','Dec']
            if not months[0][0]:
                return []
            return [month_names[int(month[0]) - 1] for month in months]
            
        except sqlite3.Error as e:
            print(f"Error getting unique month: {e}")
            return []
            
        finally:
            if conn:
                conn.close()

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
        cursor.execute('SELECT COUNT(*) FROM (SELECT ID, Nama, TanggalPeminjaman, TanggalPengembalian, TenggatPengembalian, BesarPembayaran FROM Peminjaman)')
        total_records = cursor.fetchone()[0]
        self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
        conn.close()

        # If no records, hide pagination and return empty container
        if total_records == 0:
            pagination_container.hide()
            return pagination_container
        
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

    def load_data(self):
        """Load and display data from the database with pagination."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt','Nov','Dec']

            month = self.periode_dropdown.currentText()
            offset = (self.current_page - 1) * self.items_per_page

            if month == 'All Periode' :
                cursor.execute(f'''
                    SELECT ID, Nama, TanggalPeminjaman, TanggalPengembalian, TanggalPembayaran, BesarPembayaran
                    FROM Peminjaman WHERE StatusPembayaran = 1
                    LIMIT {self.items_per_page} 
                    OFFSET {offset}
                ''')
                data = cursor.fetchall()

            else :
                idx = 0
                for i in range(12):
                    if (month_names[i] == month):
                        idx = i + 1

                cursor.execute(f'''
                    SELECT ID, Nama, TanggalPeminjaman, TanggalPengembalian, TanggalPembayaran, BesarPembayaran
                    FROM Peminjaman 
                    WHERE strftime('%m', TanggalPembayaran) = ?
                    LIMIT {self.items_per_page} 
                    OFFSET {offset}
                ''', (str(idx), ))
                data = cursor.fetchall()
            
        except sqlite3.Error as e:
            print(f"Error loading data: {e}")
            
        finally:
            if conn:
                conn.close()

    def apply_filters(self):
        """Apply filters based on the selected color and year."""
        self.load_data()

