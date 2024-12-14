import sys
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QDesktopWidget, QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit
)

class PelangganUI:
    @staticmethod
    def formPelanggan(parent, mode="create", customer_data=None):

        dialog = QDialog(parent)
        
        if parent:
            dialog.setGeometry(parent.window().geometry())
        else:
            screen = QDesktopWidget().screenGeometry()
            dialog.setGeometry(screen)
        
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setModal(True)
        
        validation_states = {
            'NIK': False,
            'Nama': False,
            'Kontak': False,
            'Alamat': False
        }
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        overlay = QWidget(dialog)
        overlay.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.85); }")
        overlay.setGeometry(dialog.geometry())
        
        content = QWidget(overlay)
        content.setFixedSize(440, 630)
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
                background-color: #F3F4F6;
                border-radius: 20px;
                margin: 0;
                padding: 0;
            }
        """)
        
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
        
        title = QLabel("Tambah Pelanggan" if mode == "create" else "Edit Pelanggan")
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
        
        header_layout.addWidget(icon_container)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        content_layout.addLayout(header_layout)
        
        inputs = {}
        error_labels = {}
        placeholders = {
            'NIK': 'Masukkan NIK (16 digit)',
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
            
            if field == 'NIK':
                input_field.setValidator(QRegExpValidator(QRegExp("^[0-9]{0,16}$")))
            elif field == 'Alamat':
                input_field.setMaxLength(30)
                
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
            
        confirm_btn = QPushButton("Yakin Wak?" if mode == "create" else "Simpan Perubahan")
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
            
            confirm_btn.setEnabled(all(validation_states.values()))
        
        for field, input_field in inputs.items():
            input_field.textChanged.connect(lambda text, f=field: validate_field(f, text))
            
        if mode == "edit" and customer_data:
            for field in inputs:
                validate_field(field, str(customer_data[field]))
        
        confirm_btn.clicked.connect(dialog.accept)
        
        main_layout.addWidget(overlay)
        
        if dialog.exec_() == QDialog.Accepted:
            return dialog, {field: input_field.text() for field, input_field in inputs.items()}
        return None, None

    @staticmethod
    def confirmPelanggan(parent, count):
        """Show confirmation dialog for deleting customers."""
        dialog = QDialog(parent)
        
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
        
        overlay = QWidget(dialog)
        overlay.setStyleSheet("QWidget { background-color: rgba(0, 0, 0, 0.85); }")
        overlay.setGeometry(dialog.geometry())
        
        content = QWidget(overlay)
        content.setFixedSize(440, 280)
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
        
        title = QLabel("Hapus Pelanggan")
        close_btn = QPushButton("×")
        close_btn.clicked.connect(dialog.reject)
        
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
        
        header_layout.addWidget
        header_layout.addWidget(icon_container)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        content_layout.addLayout(header_layout)
        
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