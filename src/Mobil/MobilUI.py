from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (
    QDialog, QDesktopWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit
)
import re


class MobilUI(QWidget):
    @staticmethod
    def formMobil(parent, mode="create", mobil_data=None):
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
        validation_states = {field: False for field in ['NomorPlat', 'Gambar', 'Model', 'Warna', 'Tahun', 'StatusKetersediaan']}
        
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
        title = QLabel("Add a Mobil" if mode == "create" else "Edit Mobil")
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
            'NomorPlat': 'Nomor Plat',
            'Gambar': 'Gambar',
            'Model': 'Model',
            'Warna': 'Warna',
            'Tahun': 'Tahun',
            'StatusKetersediaan': 'Status Ketersediaan'
        }
        
        for field in ['NomorPlat', 'Gambar', 'Model', 'Warna', 'Tahun', 'StatusKetersediaan']:
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
            if field == 'NomorPlat':
                input_field.setValidator(QRegExpValidator(QRegExp(r'[A-Z]{1,2}\s\d{1,4}\s[A-Z]{1,3}')))
            elif field == 'Tahun':
                input_field.setValidator(QRegExpValidator(QRegExp(r'\d{4}')))
            elif field == 'StatusKetersediaan':
                input_field.setValidator(QRegExpValidator(QRegExp(r'[01]')))
                
            # Set existing values in edit mode
            if mode == "edit" and mobil_data:
                input_field.setText(str(mobil_data[field]))
                
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
            
            if field == 'NomorPlat':
                is_valid = bool(re.match(r'[A-Z]{1,2}\s\d{1,4}\s[A-Z]{1,3}', text))
                message = "Nomor plat harus berupa kombinasi huruf dan angka"
            elif field == 'Tahun':
                is_valid = bool(re.match(r'\d{4}', text))
                message = "Tahun harus berupa angka 4 digit"
            elif field == 'StatusKetersediaan':
                is_valid = bool(re.match(r'[01]', text))
                message = "Status ketersediaan harus berupa angka 0 atau 1"
            else:
                is_valid = bool(text)
                message = "Field ini tidak boleh kosong"
                
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
        if mode == "edit" and mobil_data:
            for field in inputs:
                validate_field(field, str(mobil_data[field]))
        
        # Connect confirm button
        confirm_btn.clicked.connect(dialog.accept)
        
        main_layout.addWidget(overlay)
        
        # Execute dialog and return results
        if dialog.exec_() == QDialog.Accepted:
            return dialog, {field: input_field.text() for field, input_field in inputs.items()}
        return None, None

    @staticmethod
    def confirmMobil(parent, count):
        """Show confirmation dialog for deleting Cars."""
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
        title = QLabel("Hapus Mobil")
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
        warning_label = QLabel(f"Aksi ini akan menghapus {count} mobil")
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