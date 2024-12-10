import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QSizePolicy, QCheckBox, QToolButton,
    QDesktopWidget, QDialog, QLineEdit, QMessageBox, QGraphicsBlurEffect
)
from PyQt5.QtCore import Qt, QRect, QRegExp
from PyQt5.QtGui import QFont, QColor, QIcon, QRegExpValidator
import sqlite3

class AddPelangganDialog(QDialog):
    """A dialog for adding new customers with real-time validation and user feedback."""
    def __init__(self, parent=None):
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
        
        # Initialize validation states for all fields
        self.validation_states = {
            'NIK': False,
            'Nama': False,
            'Kontak': False,
            'Alamat': False
        }
        
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface with all components and layouts."""
        # Main layout setup with proper spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create semi-transparent overlay
        overlay = QWidget(self)
        overlay.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.85); }")
        overlay.setGeometry(self.geometry())
        
        # Create content container with proper sizing
        content = QWidget(overlay)
        content.setFixedSize(440, 630)
        content.setStyleSheet("QWidget { background-color: white; border-radius: 12px; }")
        
        # Center content in overlay
        content_x = (overlay.width() - content.width()) // 2
        content_y = (overlay.height() - content.height()) // 2
        content.move(content_x, content_y)
        
        # Set up content layout with proper spacing
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 24, 32, 32)
        content_layout.setSpacing(24)
        
        # Create and setup header section
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
        """Set up the header section with icon and title."""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        header_layout.setAlignment(Qt.AlignVCenter)
        
        # Create icon container
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
        
        # Create icon label
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
        
        # Create title label
        title = QLabel("Add a Pelanggan")
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
        header_layout.addWidget(icon_container)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        return header_layout

    def setup_form_fields(self, parent_layout):
        """Set up the form fields with validation."""
        # Define field placeholders
        placeholders = {
            'NIK': 'Enter 16-digit NIK number',
            'Nama': 'Enter customer name (letters only)',
            'Kontak': 'Enter contact number',
            'Alamat': 'Enter address (max 30 characters)'
        }
        
        # Create form fields
        fields = ['NIK', 'Nama', 'Kontak', 'Alamat']
        self.inputs = {}
        self.error_labels = {}
        
        for field in fields:
            # Create field container
            field_container = QWidget()
            field_layout = QVBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(4)
            
            # Create field label
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
            
            # Create input and error container
            input_error_container = QWidget()
            input_error_container.setFixedHeight(70)
            input_error_layout = QVBoxLayout(input_error_container)
            input_error_layout.setContentsMargins(0, 0, 0, 0)
            input_error_layout.setSpacing(2)
            
            # Create input field
            input_field = QLineEdit()
            input_field.setFixedHeight(44)
            input_field.setPlaceholderText(placeholders[field])
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
            
            # Create error label
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
            
            # Add components to layouts
            input_error_layout.addWidget(input_field)
            input_error_layout.addWidget(error_label)
            field_layout.addWidget(input_error_container)
            
            # Store references
            self.inputs[field] = input_field
            self.error_labels[field] = error_label
            
            # Set up field-specific validation
            if field == 'NIK':
                input_field.setValidator(QRegExpValidator(QRegExp("^[0-9]{0,16}$")))
                input_field.textChanged.connect(lambda text, f=field: self.validate_nik(text, f))
            elif field == 'Nama':
                input_field.textChanged.connect(lambda text, f=field: self.validate_nama(text, f))
            elif field == 'Kontak':
                input_field.textChanged.connect(lambda text, f=field: self.validate_kontak(text, f))
            else:  # Alamat
                input_field.setMaxLength(30)
                input_field.textChanged.connect(lambda text, f=field: self.validate_alamat(text, f))
            
            parent_layout.addWidget(field_container)

    def setup_confirm_button(self):
        """Create and set up the confirm button."""
        confirm_btn = QPushButton("Confirm")
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

    def validate_nik(self, text, field):
        """Validate NIK input to ensure it's exactly 16 digits."""
        is_valid = len(text) == 16 and text.isdigit()
        self.validation_states[field] = is_valid
        message = "NIK must be exactly 16 digits" if text and not is_valid else ""
        self.show_validation_message(field, message)
        self.update_confirm_button()

    def validate_nama(self, text, field):
        """Validate Nama input to ensure it contains only letters and spaces."""
        is_valid = bool(text) and all(c.isalpha() or c.isspace() for c in text)
        self.validation_states[field] = is_valid
        message = "Name must contain only letters" if text and not is_valid else ""
        self.show_validation_message(field, message)
        self.update_confirm_button()

    def validate_kontak(self, text, field):
        """Validate Kontak input to ensure it contains only numbers."""
        is_valid = bool(text) and text.isdigit()
        self.validation_states[field] = is_valid
        message = "Contact must contain only numbers" if text and not is_valid else ""
        self.show_validation_message(field, message)
        self.update_confirm_button()

    def validate_alamat(self, text, field):
        """Validate Alamat input to ensure it's not empty and within length limit."""
        is_valid = bool(text) and len(text) <= 30
        self.validation_states[field] = is_valid
        message = "Address must not be empty and max 30 characters" if text and not is_valid else ""
        self.show_validation_message(field, message)
        self.update_confirm_button()

    def show_validation_message(self, field, message):
        """Display validation message while maintaining layout stability."""
        error_label = self.error_labels[field]
        input_field = self.inputs[field]
        
        if message:
            error_label.setText(message)
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
            input_field.setProperty("invalid", True)
        else:
            error_label.setText("")
            error_label.setStyleSheet("""
                QLabel {
                    color: transparent;
                    font-family: 'Poly', sans-serif;
                    font-size: 12px;
                    min-height: 20px;
                    padding: 0;
                    margin: 0;
                }
            """)
            input_field.setProperty("invalid", False)
        
        # Force style update
        input_field.style().unpolish(input_field)
        input_field.style().polish(input_field)

    def update_confirm_button(self):
        """Update confirm button state based on overall form validity."""
        is_valid = all(self.validation_states.values())
        self.confirm_button.setEnabled(is_valid)

    def validate_and_accept(self):
        """Perform final validation and accept dialog if valid."""
        if all(self.validation_states.values()):
            self.accept()

    def get_data(self):
        """Retrieve the form data as a dictionary."""
        return {field: input_field.text() for field, input_field in self.inputs.items()}

class EditPelangganDialog(AddPelangganDialog):
    """A dialog for editing existing customer data."""
    def __init__(self, customer_data, parent=None):
        super().__init__(parent)
        self.customer_data = customer_data
        self.original_nik = customer_data['NIK']
        self.setup_edit_mode()

    def setup_edit_mode(self):
        """Modify the dialog for edit mode and populate fields with existing data."""
        # Update dialog title
        title_label = self.findChild(QLabel, "")
        for child in self.findChildren(QLabel):
            if child.text() == "Add a Pelanggan":
                title_label = child
                break
        if title_label:
            title_label.setText("Edit Pelanggan")

        # Update confirm button text
        if self.confirm_button:
            self.confirm_button.setText("Save Changes")

        # Populate fields with existing data
        field_mapping = {
            'NIK': self.customer_data['NIK'],
            'Nama': self.customer_data['Nama'],
            'Kontak': self.customer_data['Kontak'],
            'Alamat': self.customer_data['Alamat']
        }

        # Set existing values and validate
        for field, value in field_mapping.items():
            if field in self.inputs:
                self.inputs[field].setText(str(value))
                
                # Trigger validation for each field
                if field == 'NIK':
                    self.validate_nik(str(value), field)
                elif field == 'Nama':
                    self.validate_nama(str(value), field)
                elif field == 'Kontak':
                    self.validate_kontak(str(value), field)
                elif field == 'Alamat':
                    self.validate_alamat(str(value), field)

class PelangganController(QWidget):
    """Main controller for managing customer data with comprehensive CRUD operations."""
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
        self.pagination_buttons = []
        
        # Initialize database and UI
        self.init_database()
        self.setup_main_layout()
        self.load_data()

    def setup_window_geometry(self):
        """Configure window dimensions based on screen size."""
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.available_width = screen.width() - (screen.width() * 0.25)
        self.screen_width = screen.width()
        self.screen_height = screen.height()

    def setup_main_layout(self):
        """Initialize the main layout structure."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self.setup_table()
        layout.addWidget(self.table)
        
        bottom_layout = self.setup_bottom_controls()
        layout.addLayout(bottom_layout)

    def setup_table(self):
        """Configure the data table with proper styling and column setup."""
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "", "NIK", "Nama", "Kontak", "Alamat", "Credit Point", "Status", "Aksi"
        ])
        
        # Define and apply column widths
        column_percentages = {
            0: 5,     # Checkbox
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
        
        # Apply styling to the table
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
        
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def setup_bottom_controls(self):
        """Set up the bottom control panel with pagination and action buttons."""
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
        
        # Set up pagination controls
        pagination_container = self.setup_pagination()
        
        # Create action buttons (Add and Delete)
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
        
        # Connect button actions
        add_button.clicked.connect(self.handle_add_pelanggan)
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

    def handle_add_pelanggan(self):
        """Handle the addition of a new customer."""
        dialog = AddPelangganDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            if not all(data.values()):
                QMessageBox.warning(self, "Validation Error", "All fields are required!")
                return
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO Pelanggan (NIK, Nama, Kontak, Alamat, CreditPoint, StatusPinjam)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data['NIK'],
                    data['Nama'],
                    data['Kontak'],
                    data['Alamat'],
                    100,  # Default credit point
                    0     # Default status (not borrowing)
                ))
                
                conn.commit()
                self.load_data()
                QMessageBox.information(self, "Success", "Customer added successfully!")
                
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "NIK already exists!")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
            finally:
                if conn:
                    conn.close()

    def handle_edit(self, row):
        """Handle editing of an existing customer."""
        try:
            # Get current customer data
            customer_data = {
                'NIK': self.table.item(row, 1).text(),
                'Nama': self.table.item(row, 2).text(),
                'Kontak': self.table.item(row, 3).text(),
                'Alamat': self.table.item(row, 4).text(),
                'CreditPoint': self.table.item(row, 5).text(),
                'StatusPinjam': 1 if "Pinjam" in self.table.cellWidget(row, 6).findChild(QPushButton).text() else 0
            }

            # Create and show edit dialog
            dialog = EditPelangganDialog(customer_data, self)
            if dialog.exec_() == QDialog.Accepted:
                updated_data = dialog.get_data()
                
                if not all(updated_data.values()):
                    QMessageBox.warning(self, "Validation Error", "All fields are required!")
                    return

                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE Pelanggan 
                        SET NIK = ?, Nama = ?, Kontak = ?, Alamat = ?
                        WHERE NIK = ?
                    ''', (
                        updated_data['NIK'],
                        updated_data['Nama'],
                        updated_data['Kontak'],
                        updated_data['Alamat'],
                        customer_data['NIK']  # Original NIK for identification
                    ))
                    
                    conn.commit()
                    self.load_data()
                    QMessageBox.information(self, "Success", "Customer data updated successfully!")
                    
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, "Error", "NIK already exists!")
                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
                finally:
                    if conn:
                        conn.close()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while editing: {str(e)}")

    def handle_delete_selected(self):
        """Handle deletion of selected customers."""
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
            
            # Update pagination
            cursor.execute('SELECT COUNT(*) FROM Pelanggan')
            total_records = cursor.fetchone()[0]
            new_total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
            
            if self.current_page > new_total_pages:
                self.current_page = max(1, new_total_pages)
            
            self.load_data()
            QMessageBox.information(self, "Success", "Selected customers deleted successfully!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
            
        finally:
            if conn:
                conn.close()

    def create_status_cell(self, row, col, is_pinjam):
        """Create a status cell with appropriate styling."""
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
        """Create an action cell with edit functionality."""
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
        
        action_btn.clicked.connect(lambda: self.handle_edit(row))

    def setup_pagination(self):
        """
        Set up pagination controls for navigating through customer data.
        Creates a container with navigation buttons and page numbers.
        """
        pagination_container = QWidget()
        pagination_layout = QHBoxLayout(pagination_container)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(8)
        
        # Calculate total pages based on database records
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM Pelanggan')
        total_records = cursor.fetchone()[0]
        self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
        conn.close()
        
        # Define consistent button styling
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
        
        # Create and configure navigation buttons
        self.first_button = QPushButton("First")
        self.prev_button = QPushButton("←")
        self.next_button = QPushButton("→")
        self.last_button = QPushButton("Last")
        
        # Apply styling to navigation buttons
        for btn in [self.first_button, self.prev_button, self.next_button, self.last_button]:
            btn.setStyleSheet(button_style)
        
        # Add navigation buttons and connect their signals
        pagination_layout.addWidget(self.first_button)
        self.first_button.clicked.connect(lambda: self.go_to_page(1))
        
        pagination_layout.addWidget(self.prev_button)
        self.prev_button.clicked.connect(self.previous_page)
        
        # Create numbered page buttons
        for page in range(1, min(6, self.total_pages + 1)):
            btn = QPushButton(str(page))
            btn.setStyleSheet(button_style)
            if page == self.current_page:
                btn.setProperty("current", "true")
                btn.style().unpolish(btn)
                btn.style().polish(btn)
            btn.clicked.connect(lambda x, p=page: self.go_to_page(p))
            self.pagination_buttons.append(btn)
            pagination_layout.addWidget(btn)
        
        pagination_layout.addWidget(self.next_button)
        self.next_button.clicked.connect(self.next_page)
        
        pagination_layout.addWidget(self.last_button)
        self.last_button.clicked.connect(lambda: self.go_to_page(self.total_pages))
        
        # Initialize pagination button states
        self.update_pagination_buttons()
        return pagination_container

    def update_pagination_buttons(self):
        """
        Update the enabled/disabled state of pagination buttons based on current page.
        This ensures proper navigation limits and visual feedback.
        """
        self.first_button.setEnabled(self.current_page > 1)
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        self.last_button.setEnabled(self.current_page < self.total_pages)

        # Update page number buttons to reflect current state
        for btn in self.pagination_buttons:
            page_num = int(btn.text())
            btn.setProperty("current", page_num == self.current_page)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def go_to_page(self, page):
        """
        Navigate to a specific page number.
        
        Args:
            page: The target page number to display
        """
        if 1 <= page <= self.total_pages and page != self.current_page:
            self.current_page = page
            self.load_data()
            self.update_pagination_buttons()

    def previous_page(self):
        """Navigate to the previous page if available."""
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)

    def next_page(self):
        """Navigate to the next page if available."""
        if self.current_page < self.total_pages:
            self.go_to_page(self.current_page + 1)

    def init_database(self):
        """
        Initialize the database with required tables and sample data.
        This ensures the application has a proper data structure and initial content.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
                # Insert sample customer data
                sample_data = [
                    ('3602041211870001', 'Fariz Rifqi', '08554677321', 'Puri Indah', 100, 1),
                    ('3602041211870002', 'Razi Rachman', '08126016657', 'Pondok Furqon Sekeloa', 100, 0),
                    ('3602041211870003', 'Ahmad Dharma', '08139876543', 'Jl. Sukajadi No. 45', 75, 1),
                    ('3602041211870004', 'Siti Nurhaliza', '08567890123', 'Komplek Permata Blok A2', 90, 0),
                    ('3602041211870005', 'Budi Santoso', '08234567890', 'Jl. Dipatiukur No. 23', 100, 1),
                    ('3602041211870006', 'Diana Putri', '08198765432', 'Apartemen Sudirman Lt. 5', 85, 0),
                    ('3602041211870007', 'Eko Prasetyo', '08521234567', 'Jl. Buah Batu No. 78', 95, 1),
                    ('3602041211870008', 'Fitri Handayani', '08234567891', 'Komplek Cijagra Indah B5', 80, 0),
                    ('3602041211870010', 'Hana Safira', '08561234567', 'Perumahan Antapani Blok F7', 70, 0),
                    ('3602041211870011', 'Irfan Hakim', '08129876543', 'Jl. Setiabudi No. 67', 90, 1)
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

    def get_checkbox(self, row):
        """
        Retrieve the checkbox widget from a specific table row.
        
        Args:
            row: The row index to get the checkbox from
            
        Returns:
            QCheckBox: The checkbox widget if found, None otherwise
        """
        checkbox_container = self.table.cellWidget(row, 0)
        if checkbox_container:
            return checkbox_container.layout().itemAt(0).widget()
        return None

    def get_selected_rows(self):
        """
        Get a list of all currently selected row indices.
        
        Returns:
            list: Indices of selected rows
        """
        selected_rows = []
        for row in range(self.table.rowCount()):
            checkbox = self.get_checkbox(row)
            if checkbox and checkbox.isChecked():
                selected_rows.append(row)
        return selected_rows

    def toggle_select_all(self):
        """
        Toggle the selection state of all checkboxes in the table.
        Uses the first checkbox's state to determine the new state for all checkboxes.
        """
        first_checkbox = self.get_checkbox(0)
        if first_checkbox:
            new_state = not first_checkbox.isChecked()
            for row in range(self.table.rowCount()):
                checkbox = self.get_checkbox(row)
                if checkbox:
                    checkbox.setChecked(new_state)

    def load_data(self):
        """
        Load and display paginated customer data from the database.
        Handles data fetching, formatting, and presentation in the table.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate offset for pagination
            offset = (self.current_page - 1) * self.items_per_page
            
            # Fetch paginated data
            cursor.execute('''
                SELECT * FROM Pelanggan 
                LIMIT ? OFFSET ?
            ''', (self.items_per_page, offset))
            
            data = cursor.fetchall()
            
            # Configure table for new data
            self.table.setRowCount(len(data))
            
            # Populate table with formatted data
            for row, record in enumerate(data):
                # Create checkbox in first column
                checkbox = QCheckBox()
                checkbox_container = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_container)
                checkbox_layout.setContentsMargins(16, 16, 16, 16)
                checkbox_layout.addWidget(checkbox, alignment=Qt.AlignCenter)
                self.table.setCellWidget(row, 0, checkbox_container)
                
                # Add data cells with proper formatting
                for col, value in enumerate(record):
                    if col == 5:  # Status column
                        self.create_status_cell(row, col + 1, value == 1)
                    else:
                        item = QTableWidgetItem(str(value))
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(row, col + 1, item)
                
                # Add edit button in last column
                self.create_action_cell(row)
                
                # Set consistent row height
                self.table.setRowHeight(row, 72)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading data: {str(e)}")
            
        finally:
            if conn:
                conn.close()