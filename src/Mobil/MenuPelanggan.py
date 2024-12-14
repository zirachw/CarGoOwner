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
import sqlite3
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QCheckBox, QDesktopWidget, QMessageBox
)
from PyQt5.QtCore import Qt


@dataclass
class Pelanggan:
    """
    Class representing a customer (Pelanggan) with database operations.
    Handles all database-related functionality that was previously in PelangganController.
    """
    NIK: str
    Nama: str
    Kontak: str
    Alamat: str
    CreditPoint: int
    StatusPinjam: bool
    
    def __init__(self, schema_path: str):
        """Initialize database connection and setup"""
        self.schema_path = schema_path
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(schema_path)))
        self.db_path = os.path.join(self.base_dir, "src/CarGoOwnerPelanggan.db")
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables and sample data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Drop the existing Pelanggan table if it exists
            cursor.execute('DROP TABLE IF EXISTS Pelanggan')

            # Create the Pelanggan table with proper schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Pelanggan (
                    NIK TEXT PRIMARY KEY,
                    Nama TEXT,
                    Kontak TEXT,
                    Alamat TEXT,
                    CreditPoint INTEGER,
                    StatusPinjam BOOLEAN
                )
            ''')
            
            # Check if table needs sample data
            cursor.execute('SELECT COUNT(*) FROM Pelanggan')
            if cursor.fetchone()[0] == 0:
                # Insert sample customer data (sample_data list from original code)
                # Note: Sample data insertion code remains the same as in original
                sample_data = [
                ]
                
                cursor.executemany('''
                    INSERT INTO Pelanggan (NIK, Nama, Kontak, Alamat, CreditPoint, StatusPinjam)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', sample_data)
                
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            if conn:
                conn.close()

    def getPelanggan(self, page: int, items_per_page: int) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieve paginated customer data from the database.
        
        Args:
            page: Current page number
            items_per_page: Number of items per page
            
        Returns:
            Tuple containing list of customer data and total number of records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute('SELECT COUNT(*) FROM Pelanggan')
            total_records = cursor.fetchone()[0]
            
            # Get paginated data
            offset = (page - 1) * items_per_page
            cursor.execute('''
                SELECT * FROM Pelanggan 
                LIMIT ? OFFSET ?
            ''', (items_per_page, offset))
            
            # Convert to list of dictionaries
            columns = ['NIK', 'Nama', 'Kontak', 'Alamat', 'CreditPoint', 'StatusPinjam']
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return data, total_records
            
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving customer data: {str(e)}")
        finally:
            if conn:
                conn.close()

    def setPelanggan(self, pelanggan: Dict[str, Any], mode: str = "create") -> bool:
        """
        Create, update, or delete customer data in the database.
        
        Args:
            pelanggan: Dictionary containing customer data
            mode: Operation mode - "create", "edit", or "delete"
            
        Returns:
            bool: True if operation was successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if mode == "create":
                cursor.execute('''
                    INSERT INTO Pelanggan (NIK, Nama, Kontak, Alamat, CreditPoint, StatusPinjam)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    pelanggan['NIK'],
                    pelanggan['Nama'],
                    pelanggan['Kontak'],
                    pelanggan['Alamat'],
                    pelanggan.get('CreditPoint', 100),  # Default credit point
                    pelanggan.get('StatusPinjam', 0)    # Default status
                ))
            elif mode == "edit":
                cursor.execute('''
                    UPDATE Pelanggan 
                    SET NIK = ?, Nama = ?, Kontak = ?, Alamat = ?
                    WHERE NIK = ?
                ''', (
                    pelanggan['NIK'],
                    pelanggan['Nama'],
                    pelanggan['Kontak'],
                    pelanggan['Alamat'],
                    pelanggan['original_NIK']  # Original NIK for identification
                ))
            elif mode == "delete":
                # Support deleting a single customer or multiple customers
                niks = pelanggan['NIKs'] if isinstance(pelanggan['NIKs'], list) else [pelanggan['NIKs']]
                cursor.executemany(
                    'DELETE FROM Pelanggan WHERE NIK = ?',
                    [(nik,) for nik in niks]
                )
            else:
                raise ValueError(f"Invalid mode: {mode}")
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            raise Exception(f"Error performing database operation: {str(e)}")
        finally:
            if conn:
                conn.close()

    def getAllNIKs(self) -> set:
        """
        Get all NIKs from the database.
        
        Returns:
            set: Set of all NIKs in the database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT NIK FROM Pelanggan')
            return {row[0] for row in cursor.fetchall()}
            
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving NIKs: {str(e)}")
        finally:
            if conn:
                conn.close()

class PelangganUI:
    @staticmethod
    def formPelanggan(parent, mode="create", customer_data=None):
        """
        Create a reusable form for both creating and editing customer data.
        
        Args:
            parent: Parent widget
            mode (str): Either "create" or "edit"
            customer_data (dict, optional): Existing customer data for edit mode
            
        Returns:
            tuple: (QDialog instance, dict of form data) if accepted, (None, None) if cancelled
        """
        dialog = QDialog(parent)
        
        # Set the dialog to cover the entire screen for overlay effect
        if parent:
            dialog.setGeometry(parent.window().geometry())
        else:
            screen = QDesktopWidget().screenGeometry()
            dialog.setGeometry(screen)
        
        # Configure window properties
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setModal(True)
        
        # Initialize validation states
        validation_states = {
            'NIK': False,
            'Nama': False,
            'Kontak': False,
            'Alamat': False
        }
        
        # Main layout setup
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create semi-transparent overlay
        overlay = QWidget(dialog)
        overlay.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.85); }")
        overlay.setGeometry(dialog.geometry())
        
        # Create content container
        content = QWidget(overlay)
        content.setFixedSize(440, 630)
        content.setStyleSheet("QWidget { background-color: white; border-radius: 12px; }")
        
        # Center content
        content_x = (overlay.width() - content.width()) // 2
        content_y = (overlay.height() - content.height()) // 2
        content.move(content_x, content_y)
        
        # Content layout
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 24, 32, 32)
        content_layout.setSpacing(24)
        
        # Create header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        header_layout.setAlignment(Qt.AlignVCenter)
        
        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("""
            QFrame {
                background-color: #F3F4F6;
                border-radius: 20px;
                margin: 0;
                padding: 0;
            }
        """)
        
        # Icon label
        icon_label = QLabel(icon_container)
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setText("👥")
        icon_label.setStyleSheet("""
            QLabel {
                padding: 0;
                margin: 0;
                font-size: 20px;
            }
        """)
        
        # Title
        title = QLabel("Add a Pelanggan" if mode == "create" else "Edit Pelanggan")
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
        
        # Close button
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
        close_btn.clicked.connect(dialog.reject)
        
        # Assemble header
        header_layout.addWidget(icon_container)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        content_layout.addLayout(header_layout)
        
        # Create form fields
        inputs = {}
        error_labels = {}
        placeholders = {
            'NIK': 'Enter 16-digit NIK number',
            'Nama': 'Enter customer name (letters only)',
            'Kontak': 'Enter contact number',
            'Alamat': 'Enter address (max 30 characters)'
        }
        
        for field in ['NIK', 'Nama', 'Kontak', 'Alamat']:
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
                    margin: 0;
                    padding: 0;
                }
            """)
            field_layout.addWidget(label)
            
            input_error_container = QWidget()
            input_error_container.setFixedHeight(70)
            input_error_layout = QVBoxLayout(input_error_container)
            input_error_layout.setContentsMargins(0, 0, 0, 0)
            input_error_layout.setSpacing(2)
            
            input_field = QLineEdit()
            input_field.setFixedHeight(44)
            input_field.setPlaceholderText(placeholders[field])
            
            # Set field-specific validators
            if field == 'NIK':
                input_field.setValidator(QRegExpValidator(QRegExp("^[0-9]{0,16}$")))
            elif field == 'Alamat':
                input_field.setMaxLength(30)
                
            # Set existing values in edit mode
            if mode == "edit" and customer_data:
                input_field.setText(str(customer_data[field]))
                
            input_field.setStyleSheet("""
                QLineEdit {
                    padding: 12px;
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                    background-color: white;
                    font-family: 'Poly', sans-serif;
                    font-size: 14px;
                    margin: 0;
                }
                QLineEdit:focus {
                    border: 1px solid #9CA3AF;
                }
                QLineEdit[invalid="true"] {
                    border: 1px solid #EF4444;
                }
                QLineEdit::placeholder {
                    color: #9CA3AF;
                }
            """)
            
            error_label = QLabel()
            error_label.setFixedHeight(20)
            error_label.setStyleSheet("""
                QLabel {
                    color: #EF4444;
                    font-family: 'Poly', sans-serif;
                    font-size: 12px;
                    min-height: 20px;
                    padding: 0;
                    margin: 0;
                }
            """)
            error_label.setVisible(True)
            error_label.setWordWrap(True)
            
            input_error_layout.addWidget(input_field)
            input_error_layout.addWidget(error_label)
            field_layout.addWidget(input_error_container)
            
            inputs[field] = input_field
            error_labels[field] = error_label
            content_layout.addWidget(field_container)
            
        # Create confirm button
        confirm_btn = QPushButton("Confirm" if mode == "create" else "Save Changes")
        confirm_btn.setFixedSize(376, 44)
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
        content_layout.addWidget(confirm_btn)
        
        # Add validation logic
        def validate_field(field, text):
            """Validate individual field input."""
            is_valid = False
            message = ""
            
            if field == 'NIK':
                is_valid = len(text) == 16 and text.isdigit()
                message = "NIK must be exactly 16 digits" if text and not is_valid else ""
            elif field == 'Nama':
                is_valid = bool(text) and all(c.isalpha() or c.isspace() for c in text)
                message = "Name must contain only letters" if text and not is_valid else ""
            elif field == 'Kontak':
                is_valid = bool(text) and text.isdigit()
                message = "Contact must contain only numbers" if text and not is_valid else ""
            elif field == 'Alamat':
                is_valid = bool(text) and len(text) <= 30
                message = "Address must not be empty and max 30 characters" if text and not is_valid else ""
                
            validation_states[field] = is_valid
            error_labels[field].setText(message)
            input_field = inputs[field]
            input_field.setProperty("invalid", bool(message))
            input_field.style().unpolish(input_field)
            input_field.style().polish(input_field)
            
            # Update confirm button state
            confirm_btn.setEnabled(all(validation_states.values()))
        
        # Connect validation to text changes
        for field, input_field in inputs.items():
            input_field.textChanged.connect(lambda text, f=field: validate_field(f, text))
            
        # Initial validation for edit mode
        if mode == "edit" and customer_data:
            for field in inputs:
                validate_field(field, str(customer_data[field]))
        
        # Connect confirm button
        confirm_btn.clicked.connect(dialog.accept)
        
        main_layout.addWidget(overlay)
        
        # Execute dialog and return results
        if dialog.exec_() == QDialog.Accepted:
            return dialog, {field: input_field.text() for field, input_field in inputs.items()}
        return None, None

    @staticmethod
    def confirmPelanggan(parent, count):
        """Show confirmation dialog for deleting customers."""
        dialog = QDialog(parent)
        
        # Set dialog geometry
        if parent:
            dialog.setGeometry(parent.window().geometry())
        else:
            screen = QDesktopWidget().screenGeometry()
            dialog.setGeometry(screen)
        
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setModal(True)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create overlay
        overlay = QWidget(dialog)
        overlay.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.85); }")
        overlay.setGeometry(dialog.geometry())
        
        # Create content container
        content = QWidget(overlay)
        content.setFixedSize(440, 280)
        content.setStyleSheet("QWidget { background-color: white; border-radius: 12px; }")
        
        # Center content
        content_x = (overlay.width() - content.width()) // 2
        content_y = (overlay.height() - content.height()) // 2
        content.move(content_x, content_y)
        
        # Set up content layout
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 24, 32, 32)
        content_layout.setSpacing(24)
        
        # Create header layout
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        header_layout.setAlignment(Qt.AlignVCenter)
        
        # Add warning icon
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("""
            QFrame {
                background-color: #FEE2E2;
                border-radius: 20px;
                margin: 0;
                padding: 0;
            }
        """)
        
        icon_label = QLabel(icon_container)
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setText("👥")
        
        # Add title and close button
        title = QLabel("Hapus Pelanggan")
        close_btn = QPushButton("×")
        close_btn.clicked.connect(dialog.reject)
        
        # Style components
        icon_label.setStyleSheet("QLabel { padding: 0; margin: 0; font-size: 20px; }")
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
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        
        # Assemble header
        header_layout.addWidget
        header_layout.addWidget(icon_container)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        content_layout.addLayout(header_layout)
        
        # Warning message
        warning_label = QLabel(f"Aksi ini akan menghapus {count} pelanggan")
        warning_label.setStyleSheet("""
            QLabel {
                color: #EF4444;
                font-family: 'Poly', sans-serif;
                font-size: 14px;
                margin: 0;
                padding: 0;
            }
        """)
        warning_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(warning_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(16)
        
        confirm_btn = QPushButton("Yakin Wak?")
        confirm_btn.setFixedHeight(44)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'Poly', sans-serif;
                font-size: 14px;
                font-weight: 500;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        confirm_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QPushButton("Batal")
        cancel_btn.setFixedHeight(44)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                color: #374151;
                border: none;
                border-radius: 8px;
                font-family: 'Poly', sans-serif;
                font-size: 14px;
                font-weight: 500;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons_layout.addWidget(confirm_btn)
        buttons_layout.addWidget(cancel_btn)
        content_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(overlay)
        return dialog.exec_() == QDialog.Accepted
    
class PelangganController(QWidget):
    """
    Controller class for managing customer data display and interactions.
    Exposes only four main CRUD operations, with all helper functions nested within.
    """
    def __init__(self, schema_path, parent=None):
        super().__init__(parent)
        
        # Initialize basic properties
        self.selected_niks = set()
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.available_width = screen.width() - (screen.width() * 0.25)
        
        # Initialize model and pagination state
        self.pelanggan_model = Pelanggan(schema_path)
        self.current_page = 1
        self.items_per_page = 10
        self.pagination_buttons = []
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Initialize table
        self.table = QTableWidget()

        
        # Initial data load
        self.ShowPelanggan()
        
    def ShowPelanggan(self):
        """
        Main method for displaying customer data with pagination and interactive controls.
        This method handles two main states:
        1. Empty state - Shows a message and single add button when no data exists
        2. Populated state - Shows full table with controls when data exists
        
        The method ensures smooth transitions between these states and proper cleanup of UI elements.
        """
        try:
            # Load data from model with pagination
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
                
                # Apply modern, clean styling to the table
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
                
                # Set proportional column widths based on content type
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
                
                # Calculate and set column widths
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
                
                # Create Select All button with modern styling
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
                        # If any NIKs are not selected, select all; otherwise deselect all
                        if all_niks - self.selected_niks:
                            self.selected_niks = all_niks
                        else:
                            self.selected_niks.clear()
                        self.ShowPelanggan()  # Refresh display
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Error toggling selection: {str(e)}")
                
                select_all_btn.clicked.connect(toggle_select_all)
                
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
                        self.ShowPelanggan()
                
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
                
                # Create Add/Delete buttons with distinct styling
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
                
                # Connect action buttons
                add_button.clicked.connect(self.CreatePelanggan)
                delete_button.clicked.connect(self.DeletePelanggan)
                
                # Assemble bottom layout
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
                self.message_label = QLabel("Tidak ada data pelanggan saat ini")
                self.message_label.setAlignment(Qt.AlignCenter)
                self.message_label.setStyleSheet("""
                    font-size: 42px; 
                    font-family: 'Poly', sans-serif; 
                    color: #6B7280;
                """)
                self.main_layout.addWidget(self.message_label)

                # Add single button layout
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

            # Handle populated state
            # Set up table if needed
            if self.table.columnCount() == 0:
                setup_table()
                
            # Add table to layout
            self.main_layout.addWidget(self.table)
            
            # Populate table with data
            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                # Create checkbox
                create_checkbox(row, record['NIK'])
                
                # Add data cells
                for col, (key, value) in enumerate(record.items()):
                    if key == 'StatusPinjam':
                        create_status_cell(row, col + 1, value == 1)
                    else:
                        # Create regular data cell
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make cell read-only
                        self.table.setItem(row, col + 1, item)
                
                # Add action cell
                create_action_cell(row, record)
                
                # Set consistent row height
                self.table.setRowHeight(row, 72)
            
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
        
        # if no customers are selected, show a warning dialog
        if not self.selected_niks:
            # Create a custom message dialog with styling similar to other dialogs
            dialog = QDialog(self)
            
            # Set dialog geometry to cover the entire screen
            screen = QDesktopWidget().screenGeometry()
            dialog.setGeometry(screen)
            
            dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
            dialog.setAttribute(Qt.WA_TranslucentBackground)
            dialog.setModal(True)
            
            main_layout = QVBoxLayout(dialog)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Create overlay
            overlay = QWidget(dialog)
            overlay.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.85); }")
            overlay.setGeometry(dialog.geometry())
            
            # Create content container
            content = QWidget(overlay)
            content.setFixedSize(500, 280)
            content.setStyleSheet("QWidget { background-color: white; border-radius: 12px; }")
            
            # Center content
            content_x = (overlay.width() - content.width()) // 2
            content_y = (overlay.height() - content.height()) // 2
            content.move(content_x, content_y)
            
            # Set up content layout
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(32, 24, 32, 32)
            content_layout.setSpacing(24)
            
            # Create header layout
            header_layout = QHBoxLayout()
            header_layout.setSpacing(12)
            header_layout.setAlignment(Qt.AlignVCenter)
            
            # Add warning icon
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
            
            # Add title and close button
            title = QLabel("Peringatan")
            
            # Style components
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
            
            # Assemble header
            header_layout.addWidget(icon_container)
            header_layout.addWidget(title)
            header_layout.addStretch()
            content_layout.addLayout(header_layout)
            
            # Warning message
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
            
            # Confirm button
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
            
            # Add button to layout
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(confirm_btn)
            button_layout.addStretch()
            content_layout.addLayout(button_layout)
            
            main_layout.addWidget(overlay)
            
            # Show the dialog
            dialog.exec_()
            return
        
        # Show confirmation dialog
        if PelangganUI.confirmPelanggan(self, len(self.selected_niks)):
            try:
                # Delete selected customers from database using setPelanggan
                self.pelanggan_model.setPelanggan(
                    {'NIKs': list(self.selected_niks)}, 
                    mode="delete"
                )
                
                # Clear selection set
                self.selected_niks.clear()
                
                # Update current page if needed
                update_page_after_delete()
                
                # Refresh the display
                self.ShowPelanggan()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete customers: {str(e)}")