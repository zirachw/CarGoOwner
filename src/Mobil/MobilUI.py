from PyQt5.QtWidgets import QGridLayout, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt

class MobilUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MobilUI")
        self.setGeometry(100, 100, 800, 600)
        
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
        top_bar.addWidget(add_button)

        delete_button = QPushButton()
        delete_button.setIcon(QIcon("./src/Component/DeleteIcon.png"))
        delete_button.setStyleSheet("border: none;")
        top_bar.addWidget(delete_button)

        main_layout.addLayout(top_bar)

        # Grid layout for car cards
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)

        # Add cars to grid layout
        cars = [
            ("./src/Component/car1.jpg", "Porsche 911 GT3", "Putih", "KT 1 A", 2021, "./src/Component/GreenCheckIcon.png"),
            ("./src/Component/car2.jpg", "Pagani Huayra", "Biru", "D 1120 HX", 2021, "./src/Component/RedCrossIcon.png"),
            ("./src/Component/car3.jpg", "Esemka", "Hitam", "J 2024 OWI", 2045, "./src/Component/GreenCheckIcon.png"),
            ("./src/Component/car4.jpg", "Avanza 2005", "Cream", "D 1715 HN", 2021, "./src/Component/GreenCheckIcon.png"),
            ("./src/Component/car1.jpg", "MV3 Garuda", "Putih", "RI 1", 2024, "./src/Component/GreenCheckIcon.png"),
        ]

        for i, car in enumerate(cars):
            card = self.create_card(*car)
            self.grid_layout.addWidget(card, i // 3, i % 3)

        # Pagination
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()

        prev_button = QPushButton("<")
        prev_button.setStyleSheet("border: none; font-size: 16px;")
        pagination_layout.addWidget(prev_button)

        for i in range(1, 5):
            page_button = QPushButton(str(i))
            page_button.setStyleSheet("border: none; font-size: 16px;")
            pagination_layout.addWidget(page_button)

        next_button = QPushButton(">")
        next_button.setStyleSheet("border: none; font-size: 16px;")
        pagination_layout.addWidget(next_button)

        pagination_layout.addStretch()
        main_layout.addLayout(pagination_layout)

    def create_card(self, image_path, title, color, license_plate, year, status_icon):
        """Create a single card for a car."""
        card_widget = QWidget()
        card_widget.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-radius: 15px;
                border: 1px solid #E0E0E0;
                padding: 10px;
            }
        """)

        # Main layout of the card
        layout = QVBoxLayout(card_widget)

        # Car image
        car_image = QLabel()
        pixmap = QPixmap(image_path).scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        car_image.setPixmap(pixmap)
        car_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(car_image)

        # Car information
        title_label = QLabel(title)
        title_label.setFont(QFont("Poly", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft)

        color_label = QLabel(color)
        color_label.setFont(QFont("Poly", 12))

        license_label = QLabel(license_plate)
        license_label.setFont(QFont("Poly", 12))

        year_label = QLabel(str(year))
        year_label.setFont(QFont("Poly", 12))
        year_label.setAlignment(Qt.AlignRight)

        # Info layout
        info_layout = QVBoxLayout()
        info_layout.addWidget(title_label)
        info_layout.addWidget(color_label)
        info_layout.addWidget(license_label)

        # Bottom row with year and status
        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(info_layout)
        bottom_layout.addStretch()
        bottom_layout.addWidget(year_label)

        # Add status icon
        status_label = QLabel()
        status_pixmap = QPixmap(status_icon).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        status_label.setPixmap(status_pixmap)
        bottom_layout.addWidget(status_label)

        layout.addLayout(bottom_layout)

        return card_widget