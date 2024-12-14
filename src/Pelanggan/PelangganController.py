import sys
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
from Pelanggan.Pelanggan import Pelanggan
from Pelanggan.PelangganUI import PelangganUI

class PelangganController(QWidget):
    """
    Controller class for managing customer data display and interactions.
    Exposes only four main CRUD operations, with all helper functions nested within.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.selected_niks = set()
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.available_width = screen.width() - (screen.width() * 0.25)
        
        self.pelanggan_model = Pelanggan()
        self.current_page = 1
        self.items_per_page = 10
        self.pagination_buttons = []
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        self.table = QTableWidget()

        self.ShowPelanggan()
        
    def ShowPelanggan(self):

        try:
            data, total_records = self.pelanggan_model.getPelanggan(
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
                    "", "NIK", "Nama", "Kontak", "Alamat", "Credit Point", "Status", "Aksi"
                ])
                
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
                
                # Configure table behavior
                self.table.setShowGrid(False)
                self.table.verticalHeader().setVisible(False)
                self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
                
                column_percentages = {
                    0: 5,     # Checkbox column
                    1: 15,    # NIK
                    2: 15,    # Nama
                    3: 12,    # Kontak
                    4: 25,    # Alamat
                    5: 10,    # Credit Point
                    6: 12,    # Status
                    7: 6      # Aksi
                }
                
                for col, percentage in column_percentages.items():
                    width = int(self.available_width * (percentage / 100))
                    self.table.setColumnWidth(col, width)

            def setup_bottom_controls():
                """
                Create and configure the bottom control panel.
                Includes select/deselect all button, pagination controls, and action buttons.
                Returns the configured bottom layout.
                """
                bottom_layout = QHBoxLayout()
                
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
                
                def toggle_select_all():
                    """Handle select/deselect all functionality"""
                    try:
                        all_niks = self.pelanggan_model.getAllNIKs()
                        if all_niks - self.selected_niks:
                            self.selected_niks = all_niks
                        else:
                            self.selected_niks.clear()
                        self.ShowPelanggan()  # Refresh display
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Error toggling selection: {str(e)}")
                
                select_all_btn.clicked.connect(toggle_select_all)
                
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
                        self.ShowPelanggan()
                
                self.first_button.clicked.connect(lambda: go_to_page(1))
                self.prev_button.clicked.connect(lambda: go_to_page(self.current_page - 1))
                self.next_button.clicked.connect(lambda: go_to_page(self.current_page + 1))
                self.last_button.clicked.connect(lambda: go_to_page(self.total_pages))
                
                pagination_layout.addWidget(self.first_button)
                pagination_layout.addWidget(self.prev_button)
                
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
                
                add_button = QPushButton("+")
                delete_button = QPushButton("×")
                
                for btn, is_add in [(add_button, True), (delete_button, False)]:
                    btn.setFixedSize(56, 56)
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {('#10B981' if is_add else '#EF4444')};
                            border-radius: 28px;
                            color: white;
                            font-size: 24px;
                        }}
                        QPushButton:hover {{
                            background-color: {('#059669' if is_add else '#DC2626')};
                        }}
                    """)
                
                add_button.clicked.connect(self.CreatePelanggan)
                delete_button.clicked.connect(self.DeletePelanggan)
                
                bottom_layout.addWidget(select_all_btn)
                bottom_layout.addStretch()
                bottom_layout.addWidget(pagination_container)
                bottom_layout.addStretch()
                bottom_layout.addWidget(add_button)
                bottom_layout.addSpacing(10)
                bottom_layout.addWidget(delete_button)
                
                return bottom_layout

            def create_checkbox(row, nik):
                """Create a checkbox for row selection."""
                def handle_checkbox_change(state):
                    if state == Qt.Checked:
                        self.selected_niks.add(nik)
                    else:
                        self.selected_niks.discard(nik)
                
                checkbox = QCheckBox()
                checkbox.setChecked(nik in self.selected_niks)
                checkbox.stateChanged.connect(handle_checkbox_change)
                
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(16, 16, 16, 16)
                layout.addWidget(checkbox, alignment=Qt.AlignCenter)
                self.table.setCellWidget(row, 0, container)

            def create_status_cell(row, col, is_pinjam):
                """Create a status indicator cell."""
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

            def create_action_cell(row, record):
                """Create an action cell with edit button."""
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
                
                action_btn.clicked.connect(lambda: self.EditPelanggan(record))
                
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.setContentsMargins(16, 16, 16, 16)
                layout.addWidget(action_btn, alignment=Qt.AlignCenter)
                self.table.setCellWidget(row, 7, container)

            def clear_current_view():
                """Remove all existing widgets and layouts."""
                if hasattr(self, 'message_label'):
                    self.message_label.setParent(None)
                    delattr(self, 'message_label')
                
                if hasattr(self, 'initial_layout'):
                    while self.initial_layout.count():
                        item = self.initial_layout.takeAt(0)
                        if item.widget():
                            item.widget().setParent(None)
                    self.initial_layout.setParent(None)
                    delattr(self, 'initial_layout')
                
                if self.table.parent():
                    self.main_layout.removeWidget(self.table)
                
                if hasattr(self, 'bottom_layout'):
                    while self.bottom_layout.count():
                        item = self.bottom_layout.takeAt(0)
                        if item.widget():
                            item.widget().setParent(None)
                    self.main_layout.removeItem(self.bottom_layout)
                    self.bottom_layout.setParent(None)

            self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
            clear_current_view()

            if not data:
                self.message_label = QLabel("Tidak ada data pelanggan saat ini")
                self.message_label.setAlignment(Qt.AlignCenter)
                self.message_label.setStyleSheet("""
                    font-size: 42px; 
                    font-family: 'Poly', sans-serif; 
                    color: #6B7280;
                """)
                self.main_layout.addWidget(self.message_label)

                self.initial_layout = QHBoxLayout()
                add_button = QPushButton("+")
                add_button.setFixedSize(56, 56)
                add_button.setStyleSheet("""
                    QPushButton {
                        background-color: #10B981;
                        border-radius: 28px;
                        color: white;
                        font-size: 24px;
                    }
                    QPushButton:hover {
                        background-color: #059669;
                    }
                """)
                add_button.clicked.connect(self.CreatePelanggan)
                self.initial_layout.addStretch()
                self.initial_layout.addWidget(add_button)
                self.initial_layout.addSpacing(10)
                self.main_layout.addLayout(self.initial_layout)
                
                return

            if self.table.columnCount() == 0:
                setup_table()
                
            self.main_layout.addWidget(self.table)
            
            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                create_checkbox(row, record['NIK'])
                
                for col, (key, value) in enumerate(record.items()):
                    if key == 'StatusPinjam':
                        create_status_cell(row, col + 1, value == 1)
                    else:
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make cell read-only
                        self.table.setItem(row, col + 1, item)
                
                create_action_cell(row, record)
                
                self.table.setRowHeight(row, 72)
            
            self.bottom_layout = setup_bottom_controls()
            self.main_layout.addLayout(self.bottom_layout)
            
            self.first_button.setEnabled(self.current_page > 1)
            self.prev_button.setEnabled(self.current_page > 1)
            self.next_button.setEnabled(self.current_page < self.total_pages)
            self.last_button.setEnabled(self.current_page < self.total_pages)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading data: {str(e)}")

    def CreatePelanggan(self):
        """Create a new customer record."""
        def validate_data(data):
            """Validate the customer data before creation."""
            if not all(data.values()):
                QMessageBox.warning(self, "Validation Error", "All fields are required!")
                return False
            return True
        
        dialog, data = PelangganUI.formPelanggan(self, mode="create")
        
        if dialog and data and validate_data(data):
            try:
                self.pelanggan_model.setPelanggan(data)
                self.ShowPelanggan()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create customer: {str(e)}")

    def EditPelanggan(self, customer_data):
        """Edit an existing customer record."""
        def prepare_update_data(updated_data):
            """Prepare the data for updating in database."""
            if not all(updated_data.values()):
                raise ValueError("All fields are required!")
            updated_data['original_NIK'] = customer_data['NIK']
            return updated_data
        
        try:
            dialog, updated_data = PelangganUI.formPelanggan(
                self, 
                mode="edit", 
                customer_data=customer_data
            )
            
            if dialog and updated_data:
                try:
                    prepared_data = prepare_update_data(updated_data)
                    self.pelanggan_model.setPelanggan(prepared_data, mode="edit")
                    self.ShowPelanggan()

                except ValueError as ve:
                    QMessageBox.warning(self, "Validation Error", str(ve))
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update customer: {str(e)}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during edit: {str(e)}")

    def DeletePelanggan(self):
        """Delete selected customers."""
        def update_page_after_delete():
            """Update current page after deletion."""
            total_records = self.pelanggan_model.getPelanggan(1, 1)[1]
            new_total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
            self.current_page = max(1, min(self.current_page, new_total_pages))
        
        if not self.selected_niks:
            dialog = QDialog(self)
            
            screen = QDesktopWidget().screenGeometry()
            dialog.setGeometry(screen)
            
            dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
            dialog.setAttribute(Qt.WA_TranslucentBackground)
            dialog.setModal(True)
            
            main_layout = QVBoxLayout(dialog)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            overlay = QWidget(dialog)
            overlay.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.85); }")
            overlay.setGeometry(dialog.geometry())
            
            content = QWidget(overlay)
            content.setFixedSize(500, 280)
            content.setStyleSheet("QWidget { background-color: white; border-radius: 12px; }")
            
            content_x = (overlay.width() - content.width()) // 2
            content_y = (overlay.height() - content.height()) // 2
            content.move(content_x, content_y)
            
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(32, 24, 32, 32)
            content_layout.setSpacing(24)
            
            header_layout = QHBoxLayout()
            header_layout.setSpacing(12)
            header_layout.setAlignment(Qt.AlignVCenter)
            
            icon_container = QFrame()
            icon_container.setFixedSize(40, 40)
            icon_container.setStyleSheet("""
                QFrame {
                    background-color: #4B5563;
                    border-radius: 20px;
                    margin: 0;
                    padding: 0;
                }
            """)
            
            icon_label = QLabel(icon_container)
            icon_label.setFixedSize(40, 40)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setText("⚠️")
            
            title = QLabel("Peringatan")
            
            icon_label.setStyleSheet("QLabel { padding-bottom: 4px; margin: 0; font-size: 20px; }")
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
            
            header_layout.addWidget(icon_container)
            header_layout.addWidget(title)
            header_layout.addStretch()
            content_layout.addLayout(header_layout)
            
            warning_label = QLabel("Silakan pilih setidaknya satu pelanggan untuk dihapus")
            warning_label.setStyleSheet("""
                QLabel {
                    color: #374151;
                    font-family: 'Poly', sans-serif;
                    font-size: 16px;
                    text-align: center;
                    margin: 0;
                    padding: 0;
                }
            """)
            warning_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(warning_label)
            
            confirm_btn = QPushButton("Mengerti")
            confirm_btn.setFixedHeight(44)
            confirm_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4B5563;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-family: 'Poly', sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 0 24px;
                }
                QPushButton:hover {
                    background-color: #374151;
                }
            """)
            confirm_btn.clicked.connect(dialog.accept)
            
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(confirm_btn)
            button_layout.addStretch()
            content_layout.addLayout(button_layout)
            
            main_layout.addWidget(overlay)
            
            dialog.exec_()
            return
        
        if PelangganUI.confirmPelanggan(self, len(self.selected_niks)):
            try:
                self.pelanggan_model.setPelanggan(
                    {'NIKs': list(self.selected_niks)}, 
                    mode="delete"
                )
                
                self.selected_niks.clear()
                
                update_page_after_delete()
                
                self.ShowPelanggan()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete customers: {str(e)}")