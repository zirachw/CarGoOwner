from PyQt5.QtWidgets import QGridLayout, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt
from Mobil.MobilController import MobilController  # Use absolute import
from Components.Card import CarCard  # Use absolute import

class MobilUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MobilUI")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize MobilController
        self.controller = MobilController(schema_path="src/schema.sql")
        
        # Main container widget
        main_layout = QVBoxLayout(self)
        
        # Top bar (Category dropdown + buttons)
        top_bar = QHBoxLayout()

        category_dropdown = QComboBox()
        category_dropdown.addItems(["All Category", "Sport", "SUV", "Sedan"])
        category_dropdown.setFont(QFont("Poly", 12))
        category_dropdown.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #DADADA;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
        """)
        top_bar.addWidget(category_dropdown)

        top_bar.addStretch()

        add_button = QPushButton()
        add_button.setIcon(QIcon("./src/Component/AddIcon.png"))
        add_button.setStyleSheet("border: none;")
        add_button.clicked.connect(self.add_mobil)
        top_bar.addWidget(add_button)

        delete_button = QPushButton()
        delete_button.setIcon(QIcon("./src/Component/DeleteIcon.png"))
        delete_button.setStyleSheet("border: none;")
        delete_button.clicked.connect(self.delete_mobil)
        top_bar.addWidget(delete_button)

        main_layout.addLayout(top_bar)

        # Grid layout for car cards
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)

        # Load cars from database
        self.load_cars()

        # Pagination
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()

        prev_button = QPushButton("<")
        prev_button.setStyleSheet("border: none; font-size: 16px;")
        prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(prev_button)

        for i in range(1, 5):
            page_button = QPushButton(str(i))
            page_button.setStyleSheet("border: none; font-size: 16px;")
            page_button.clicked.connect(lambda _, page=i: self.go_to_page(page))
            pagination_layout.addWidget(page_button)

        next_button = QPushButton(">")
        next_button.setStyleSheet("border: none; font-size: 16px;")
        next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(next_button)

        pagination_layout.addStretch()
        main_layout.addLayout(pagination_layout)

    def load_cars(self, page=1):
        """Load cars from the database and display them."""
        self.grid_layout.setParent(None)
        self.grid_layout = QGridLayout()
        self.layout().addLayout(self.grid_layout)

        cars = self.controller.list_mobil(limit=6, offset=(page-1)*6)
        for i, car in enumerate(cars):
            card = CarCard(
                car.gambar,
                car.model,
                car.warna,
                car.nomor_plat,
                car.tahun,
                car.status_ketersediaan
            )
            self.grid_layout.addWidget(card, i // 3, i % 3)

    def add_mobil(self):
        """Add a new Mobil."""
        # Implement the logic to add a new Mobil
        pass

    def delete_mobil(self):
        """Delete a selected Mobil."""
        # Implement the logic to delete a selected Mobil
        pass

    def prev_page(self):
        """Go to the previous page."""
        # Implement the logic to go to the previous page
        pass

    def next_page(self):
        """Go to the next page."""
        # Implement the logic to go to the next page
        pass

    def go_to_page(self, page):
        """Go to a specific page."""
        self.load_cars(page)