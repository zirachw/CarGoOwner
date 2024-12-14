import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QSizePolicy, QCheckBox, QToolButton,
    QDesktopWidget, QDialog, QLineEdit, QMessageBox, QGraphicsBlurEffect
)
from PyQt5.QtCore import Qt, QRect, QRegExp
from PyQt5.QtGui import QFont, QColor, QIcon, QRegExpValidator
import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from Peminjaman.Peminjaman import Peminjaman
from Notifikasi.NotifikasiController import NotifikasiController

class NotifikasiUI(QWidget):
    def __init__(self, parent=None):
        self.control = NotifikasiController()
        self.state = self.control.getNotifTask()
    
    def currentState (self):
        return self.state

class PengembalianUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.availableWidth = screen.width() - (screen.width() * 0.25)
        
        self.UI = NotifikasiUI()
        self.UI = self.UI.currentState()

        self.peminjaman = Peminjaman()
        self.current_page = 1
        self.items_per_page = 10
        self.pagination_buttons = []
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        self.table = QTableWidget()
        self.state = "Jadwal Pengembalian"

        self.ShowJadwalPengembalian()

    def ShowJadwalPengembalian(self):
        try:
            data, total_records = self.peminjaman.FilterNotifikasi(
                self.state,
                self.current_page, 
                self.items_per_page
            )
            def setup_table():
                """
                Configure the table structure and styling.
                Sets up columns, headers, and visual appearance of the table.
                """
                self.table.setColumnCount(8)
                self.table.setHorizontalHeaderLabels([
                    "ID", "NIK", "Nama", "Kontak", "Nomor Plat", "Tanggal Peminjaman", "Tanggal Pengembalian", "Status Pengembalian"
                ])
                
                # Apply modern, clean styling to the table
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
                
                # Configure table behavior
                self.table.setShowGrid(False)
                self.table.verticalHeader().setVisible(False)
                self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
                
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
                
                for col, percentage in column_percentages.items():
                    width = int(self.availableWidth * (percentage / 100))
                    self.table.setColumnWidth(col, width)

            def setup_bottom_controls():
                """
                Create and configure the bottom control panel.
                Includes select/deselect all button, pagination controls, and action buttons.
                Returns the configured bottom layout.
                """
                bottom_layout = QHBoxLayout()

                pagination_container = QWidget()
                pagination_layout = QHBoxLayout(pagination_container)
                pagination_layout.setContentsMargins(0, 0, 0, 0)
                pagination_layout.setSpacing(8)
                
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
                
                self.first_button = QPushButton("First")
                self.prev_button = QPushButton("←")
                self.next_button = QPushButton("→")
                self.last_button = QPushButton("Last")
                
                for btn in [self.first_button, self.prev_button, self.next_button, self.last_button]:
                    btn.setStyleSheet(button_style)
                
                def go_to_page(page):
                    """Handle pagination navigation"""
                    if 1 <= page <= self.total_pages and page != self.current_page:
                        self.current_page = page
                        self.ShowJadwalPengembalian()
                
                # Connect navigation buttons
                self.first_button.clicked.connect(lambda: go_to_page(1))
                self.prev_button.clicked.connect(lambda: go_to_page(self.current_page - 1))
                self.next_button.clicked.connect(lambda: go_to_page(self.current_page + 1))
                self.last_button.clicked.connect(lambda: go_to_page(self.total_pages))
                
                # Add navigation buttons to layout
                pagination_layout.addWidget(self.first_button)
                pagination_layout.addWidget(self.prev_button)
                
                # Add page number buttons
                def create_page_buttons():
                    """Create the numbered page buttons"""
                    window_size = 5
                    half_window = window_size // 2
                    
                    if self.total_pages <= window_size:
                        start_page, end_page = 1, self.total_pages
                    else:
                        start_page = max(1, self.current_page - half_window)
                        end_page = min(self.total_pages, start_page + window_size - 1)
                        if end_page - start_page + 1 < window_size:
                            start_page = max(1, end_page - window_size + 1)
                    
                    for page in range(start_page, end_page + 1):
                        btn = QPushButton(str(page))
                        btn.setStyleSheet(button_style)
                        if page == self.current_page:
                            btn.setProperty("current", "true")
                            btn.style().unpolish(btn)
                            btn.style().polish(btn)
                        btn.clicked.connect(lambda x, p=page: go_to_page(p))
                        pagination_layout.addWidget(btn)
                
                create_page_buttons()
                
                pagination_layout.addWidget(self.next_button)
                pagination_layout.addWidget(self.last_button)
                
                # Assemble bottom layout
                bottom_layout.addStretch()
                bottom_layout.addWidget(pagination_container)
                bottom_layout.addStretch()
                
                return bottom_layout

            def create_status_cell(row, col, is_kembali):
                """Create a status indicator cell."""
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

            def clear_current_view():
                """Remove all existing widgets and layouts."""
                # Remove message label if it exists
                if hasattr(self, 'message_label'):
                    self.message_label.setParent(None)
                    delattr(self, 'message_label')
                
                # Remove initial layout with single add button if it exists
                if hasattr(self, 'initial_layout'):
                    while self.initial_layout.count():
                        item = self.initial_layout.takeAt(0)
                        if item.widget():
                            item.widget().setParent(None)
                    self.initial_layout.setParent(None)
                    delattr(self, 'initial_layout')
                
                # Remove table if it exists
                if self.table.parent():
                    self.main_layout.removeWidget(self.table)
                
                # Remove bottom layout if it exists
                if hasattr(self, 'bottom_layout'):
                    while self.bottom_layout.count():
                        item = self.bottom_layout.takeAt(0)
                        if item.widget():
                            item.widget().setParent(None)
                    self.main_layout.removeItem(self.bottom_layout)
                    self.bottom_layout.setParent(None)

            # Main execution starts here
            # Clear existing view before showing new state
            self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
            clear_current_view()

            # Handle empty state
            if not data:
                # Show "no data" message
                self.message_label = QLabel("Tidak Ada Notifikasi Jadwal Pengembalian Saat Ini")
                self.message_label.setAlignment(Qt.AlignCenter)
                self.message_label.setStyleSheet("""
                    font-size: 42px; 
                    font-family: 'Poly', sans-serif; 
                    color: #6B7280;
                """)
                self.main_layout.addWidget(self.message_label)
                
                return

            # Handle populated state
            # Set up table if needed
            if self.table.columnCount() == 0:
                setup_table()
                
            # Add table to layout
            self.main_layout.addWidget(self.table)
            
            # Populate table with data
            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                # Add data cells
                for col, (key,value) in enumerate(record.items()):
                    if key == "StatusPengembalian":  # Status column
                        create_status_cell(row, col, value == 1)
                    else:
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(row, col, item)
                
                # Set row height
                self.table.setRowHeight(row, 115)
            
            # Set up bottom controls
            self.bottom_layout = setup_bottom_controls()
            self.main_layout.addLayout(self.bottom_layout)
            
            # Update navigation button states
            self.first_button.setEnabled(self.current_page > 1)
            self.prev_button.setEnabled(self.current_page > 1)
            self.next_button.setEnabled(self.current_page < self.total_pages)
            self.last_button.setEnabled(self.current_page < self.total_pages)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading data: {str(e)}")

    

class PembayaranUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize basic properties
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.availableWidth = screen.width() - (screen.width() * 0.25)
        
        self.control = NotifikasiController()
        self.UI = NotifikasiUI()
        self.UI = self.UI.currentState()

        # Initialize model and pagination state
        self.peminjaman = Peminjaman()
        self.current_page = 1
        self.items_per_page = 10
        self.pagination_buttons = []
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.state = "Pembayaran Rental"
        
        # Initialize table
        self.table = QTableWidget()

        self.ShowPembayaranRental()

    def ShowPembayaranRental(self):
        try:
            # Load data from model with pagination
            data, total_records = self.peminjaman.FilterNotifikasi(
                self.state,
                self.current_page, 
                self.items_per_page
            )
            print("apalah")
            print(data)
            def setup_table():
                """
                Configure the table structure and styling.
                Sets up columns, headers, and visual appearance of the table.
                """
                self.table.setColumnCount(8)
                self.table.setHorizontalHeaderLabels([
                    "ID", "NIK", "Nama", "Kontak", "Nomor Plat", "Tenggat Pembayaran", "Besar Pembayaran", "Status Pembayaran"
                ])
                
                # Apply modern, clean styling to the table
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
                
                # Configure table behavior
                self.table.setShowGrid(False)
                self.table.verticalHeader().setVisible(False)
                self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
                
                # Set proportional column widths based on content type
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
                
                # Calculate and set column widths
                for col, percentage in column_percentages.items():
                    width = int(self.availableWidth * (percentage / 100))
                    self.table.setColumnWidth(col, width)

            def setup_bottom_controls():
                """
                Create and configure the bottom control panel.
                Includes select/deselect all button, pagination controls, and action buttons.
                Returns the configured bottom layout.
                """
                bottom_layout = QHBoxLayout()
                
                # Create pagination container
                pagination_container = QWidget()
                pagination_layout = QHBoxLayout(pagination_container)
                pagination_layout.setContentsMargins(0, 0, 0, 0)
                pagination_layout.setSpacing(8)
                
                # Define common button styling
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
                
                # Create navigation buttons
                self.first_button = QPushButton("First")
                self.prev_button = QPushButton("←")
                self.next_button = QPushButton("→")
                self.last_button = QPushButton("Last")
                
                for btn in [self.first_button, self.prev_button, self.next_button, self.last_button]:
                    btn.setStyleSheet(button_style)
                
                def go_to_page(page):
                    """Handle pagination navigation"""
                    if 1 <= page <= self.total_pages and page != self.current_page:
                        self.current_page = page
                        self.ShowPembayaranRental()
                
                # Connect navigation buttons
                self.first_button.clicked.connect(lambda: go_to_page(1))
                self.prev_button.clicked.connect(lambda: go_to_page(self.current_page - 1))
                self.next_button.clicked.connect(lambda: go_to_page(self.current_page + 1))
                self.last_button.clicked.connect(lambda: go_to_page(self.total_pages))
                
                # Add navigation buttons to layout
                pagination_layout.addWidget(self.first_button)
                pagination_layout.addWidget(self.prev_button)
                
                # Add page number buttons
                def create_page_buttons():
                    """Create the numbered page buttons"""
                    window_size = 5
                    half_window = window_size // 2
                    
                    if self.total_pages <= window_size:
                        start_page, end_page = 1, self.total_pages
                    else:
                        start_page = max(1, self.current_page - half_window)
                        end_page = min(self.total_pages, start_page + window_size - 1)
                        if end_page - start_page + 1 < window_size:
                            start_page = max(1, end_page - window_size + 1)
                    
                    for page in range(start_page, end_page + 1):
                        btn = QPushButton(str(page))
                        btn.setStyleSheet(button_style)
                        if page == self.current_page:
                            btn.setProperty("current", "true")
                            btn.style().unpolish(btn)
                            btn.style().polish(btn)
                        btn.clicked.connect(lambda x, p=page: go_to_page(p))
                        pagination_layout.addWidget(btn)
                
                create_page_buttons()
                
                pagination_layout.addWidget(self.next_button)
                pagination_layout.addWidget(self.last_button)
                
                # Assemble bottom layout
                bottom_layout.addStretch()
                bottom_layout.addWidget(pagination_container)
                bottom_layout.addStretch()
                
                return bottom_layout

            def create_status_cell(row, col, is_bayar):
                """Create a status indicator cell."""
                status_text = "Sudah" if is_bayar else "Belum"
                status_btn = QPushButton(status_text)
                
                status_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {'#D1FAE5' if is_bayar else '#FEE2E2'};
                        color: {'#10B981' if is_bayar else '#EF4444'};
                        border: 1px solid {'#10B981' if is_bayar else '#EF4444'};
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

            def clear_current_view():
                """Remove all existing widgets and layouts."""
                # Remove message label if it exists
                if hasattr(self, 'message_label'):
                    self.message_label.setParent(None)
                    delattr(self, 'message_label')
                
                # Remove initial layout with single add button if it exists
                if hasattr(self, 'initial_layout'):
                    while self.initial_layout.count():
                        item = self.initial_layout.takeAt(0)
                        if item.widget():
                            item.widget().setParent(None)
                    self.initial_layout.setParent(None)
                    delattr(self, 'initial_layout')
                
                # Remove table if it exists
                if self.table.parent():
                    self.main_layout.removeWidget(self.table)
                
                # Remove bottom layout if it exists
                if hasattr(self, 'bottom_layout'):
                    while self.bottom_layout.count():
                        item = self.bottom_layout.takeAt(0)
                        if item.widget():
                            item.widget().setParent(None)
                    self.main_layout.removeItem(self.bottom_layout)
                    self.bottom_layout.setParent(None)

            # Main execution starts here
            # Clear existing view before showing new state
            self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
            clear_current_view()

            # Handle empty state
            if not data:
                # Show "no data" message
                self.message_label = QLabel("Tidak Ada Notifikasi Jadwal Pengembalian Saat Ini")
                self.message_label.setAlignment(Qt.AlignCenter)
                self.message_label.setStyleSheet("""
                    font-size: 42px; 
                    font-family: 'Poly', sans-serif; 
                    color: #6B7280;
                """)
                self.main_layout.addWidget(self.message_label)
                
                return

            # Handle populated state
            # Set up table if needed
            if self.table.columnCount() == 0:
                setup_table()
                
            # Add table to layout
            self.main_layout.addWidget(self.table)
            
            # Populate table with data
            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                # Add data cells
                for col, (key,value) in enumerate(record.items()):
                    if key == "StatusPembayaran":  # Status column
                        create_status_cell(row, col, value == 1)
                    else:
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(row, col, item)
                
                # Set row height
                self.table.setRowHeight(row, 115)
            
            # Set up bottom controls
            self.bottom_layout = setup_bottom_controls()
            self.main_layout.addLayout(self.bottom_layout)
            
            # Update navigation button states
            self.first_button.setEnabled(self.current_page > 1)
            self.prev_button.setEnabled(self.current_page > 1)
            self.next_button.setEnabled(self.current_page < self.total_pages)
            self.last_button.setEnabled(self.current_page < self.total_pages)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading data: {str(e)}")