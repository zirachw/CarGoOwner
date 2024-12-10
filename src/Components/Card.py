from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize

class CarCard(QWidget):
    def __init__(self, image_path, title, color, license_plate, year, status_icon, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget#CarCard {
                background-color: #FFFFFF;
                border-radius: 15px;
                border: 1px solid #E0E0E0;
                padding: 15px;
            }
            QLabel {
                border: none;  # Ensure no border for QLabel components
            }
        """)

        # Main layout of the card
        layout = QVBoxLayout(self)

        # Car image
        car_image = QLabel()
        try:
            pixmap = QPixmap(image_path).scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            car_image.setPixmap(pixmap)
        except Exception as e:
            print(f"Error loading image: {e}")
        car_image.setAlignment(Qt.AlignCenter)
        layout.addWidget(car_image)

        # Car information
        title_label = QLabel(title)
        title_label.setFont(QFont("Poly", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft)

        color_label = QLabel(color)
        color_label.setFont(QFont("Poly", 16))

        license_label = QLabel(license_plate)
        license_label.setFont(QFont("Poly", 16))

        year_label = QLabel(str(year))
        year_label.setFont(QFont("Poly", 16))
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
        try:
            status_icon_path = "./src/Component/GreenCheckIcon.png" if status_icon == 1 else "./src/Component/RedCrossIcon.png"
            status_pixmap = QPixmap(status_icon_path).scaled(QSize(24, 24), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            status_label.setPixmap(status_pixmap)
        except Exception as e:
            print(f"Error loading status icon: {e}")
        bottom_layout.addWidget(status_label)

        layout.addLayout(bottom_layout)