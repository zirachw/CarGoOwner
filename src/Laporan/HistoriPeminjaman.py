import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                           QFrame, QSizePolicy, QCheckBox, QToolButton, QDesktopWidget)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QColor, QIcon
import sqlite3
from pathlib import Path

class HistoriPeminjamanUI(QWidget):
    def __init__(self, parent=None):
        """Initialize the Pelanggan (Customer) UI with complete styling and functionality."""
        super().__init__(parent)
        
        # Initialize screen dimensions and layout calculations
        self.ShowLaporanPeminjamanUI()
        self.available_width = self.available_width
        self.screen_width = self.screen_width
        self.screen_height = self.screen_height
        
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
        
        # Create main layout with proper spacing
        self.setup_main_layout()
        
        # Load the initial data
        self.load_data()

    def ShowLaporanPeminjamanUI(self):
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

        top_bar = self.setup_top_bar()
        layout.addLayout(top_bar)
        
        # Initialize and setup the table
        self.setup_table()
        layout.addWidget(self.table)
        
        # Setup bottom controls (pagination, buttons)
        bottom_layout = self.setup_bottom_controls()
        layout.addLayout(bottom_layout)

    def setup_table(self):
        """Set up the table with calculated column widths based on screen size."""
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Plat", "NIK", "Nama", "Kontak", "Tanggal Peminjaman", "Tanggal Pengembalian", "Tenggat Pengembalian"
        ])
        
        column_percentages = {
            0: 5,     # Checkbox
            1: 10,    # NIK
            2: 15,    # Nama
            3: 12,    # Kontak
            4: 10,    # Alamat
            5: 16,    # Credit Point
            6: 16,    # Status
            7: 16      # Aksi
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

    def setup_top_bar(self):
        top_bar = QHBoxLayout()

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
        top_bar.addStretch()

        return top_bar

    def get_unique_month(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT strftime('%m' ,TanggalPeminjaman) AS bulan FROM Peminjaman")
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
        cursor.execute('SELECT COUNT(*) FROM (SELECT NomorPlat, Model, Warna, Tahun, StatusKetersediaan FROM Mobil)')
        total_records = cursor.fetchone()[0]
        self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
        conn.close()
        
        # Style for all pagination buttons
        button_style = """
            QPushButton {
                background: none;
                border: none;
                color: #374151;init
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
                    SELECT ID, NomorPlat, NIK, Nama, Kontak, TanggalPeminjaman, TanggalPengembalian, TenggatPengembalian
                    FROM Peminjaman
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
                    SELECT ID, NomorPlat, NIK, Nama, Kontak, TanggalPeminjaman, TanggalPengembalian, TenggatPengembalian
                    FROM Peminjaman
                    WHERE strftime('%m', TanggalPeminjaman) = ?
                    LIMIT {self.items_per_page} 
                    OFFSET {offset}
                ''', (str(idx), ))
                data = cursor.fetchall()               
            
            # Set up table rows
            self.table.setRowCount(len(data))
            for row, record in enumerate(data):                
                # Add data cells
                for col, value in enumerate(record):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, col, item)
                
                # Set row height
                self.table.setRowHeight(row, 72)
            
        except sqlite3.Error as e:
            print(f"Error loading data: {e}")
            
        finally:
            if conn:
                conn.close()

    def apply_filters(self):
        """Apply filters based on the selected color and year."""
        self.load_data()

