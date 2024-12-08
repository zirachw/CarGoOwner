import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class PeminjamanUI(QWidget):
    def __init__(self, schema_path="src/schema.sql", parent=None):
        super().__init__(parent)
        self.schema_path = schema_path
        self.init_ui()
        self.init_database()
        self.load_data()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Daftar Peminjaman")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(title)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nama", "NIK", "Nomor Plat", "Kontak", 
            "Tanggal\nPeminjaman", "Tanggal\nPengembalian", 
            "Tanggal\nPembayaran", "Tenggat\nPengembalian", 
            "Besar\nPembayaran", "Status\nPengembalian", "Status\nPembayaran"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Enable word wrapping for headers
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                word-wrap: break-word;  /* Enable word wrapping */
                background-color: #f9f9f9;
                font-weight: bold;
                border: 1px solid #dddddd;
                padding: 5px;
                text-align: center;  /* Center align header text */
                font-size: 12px;
            }
        """)

        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dddddd;
                border: 1px solid #dddddd;
            }
        """)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.verticalHeader().setVisible(False)  # Hide vertical header
        layout.addWidget(self.table)

    def init_database(self):
        """Initialize the database using schema.sql."""
        conn = sqlite3.connect('src/CarGoOwner.db')
        cursor = conn.cursor()

        # Execute the schema.sql file
        try:
            with open(self.schema_path, 'r') as f:
                schema = f.read()
            cursor.executescript(schema)
            print(f"Database initialized using {self.schema_path}")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            conn.commit()
            conn.close()

    def load_data(self):
        """Load data from the database into the table."""
        conn = sqlite3.connect('src/CarGoOwner.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Peminjaman')
        data = cursor.fetchall()

        self.table.setRowCount(len(data))
        for row, record in enumerate(data):
            for col, value in enumerate(record):
                if col in [10, 11]:  # Status Pengembalian and Status Pembayaran columns
                    # Checkbox-like display
                    item = QTableWidgetItem("✓" if value else "✗")
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(QColor('#4CAF50') if value else QColor('#F44336'))
                else:
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        conn.close()
