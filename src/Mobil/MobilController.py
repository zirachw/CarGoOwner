from PyQt5.QtWidgets import QGridLayout, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QGraphicsDropShadowEffect, QCheckBox, QMessageBox, QDialog
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush
from PyQt5.QtCore import Qt, QSize, QRect
from Mobil.MobilUI import MobilUI  # Ensure correct import
from Mobil.Mobil import Mobil  # Ensure correct import
import sqlite3

class MobilController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MobilUI")
        self.setGeometry(100, 100, 800, 600)
        
        # Main container widget
        main_layout = QVBoxLayout(self)

        self.pagination_buttons = []  # Store pagination buttons

        self.mobil = Mobil()
        
        # Initialize navigation button references
        self.first_button = None
        self.prev_button = None
        self.next_button = None
        self.last_button = None
        
        # Set items per page
        self.items_per_page = 6
        self.current_page = 1
        
        # Top bar (Category dropdown + buttons)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(10, 10, 10, 20)  # Add bottom padding to the top bar layout

        # Color dropdown
        self.color_dropdown = QComboBox()
        self.color_dropdown.setFont(QFont("Poly", 12))
        self.color_dropdown.setStyleSheet("""
            QComboBox {
                padding: 8px;
                padding-left: 20px;
                border: 1px solid #D1D5DB;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
        """)
        self.color_dropdown.addItem("All Colors")
        self.color_dropdown.addItems(self.mobil.get_unique_colors())
        self.color_dropdown.currentIndexChanged.connect(self.showMobil)
        top_bar.addWidget(self.color_dropdown)

        # Year dropdown
        self.year_dropdown = QComboBox()
        self.year_dropdown.setFont(QFont("Poly", 12))
        self.year_dropdown.setStyleSheet("""
            QComboBox {
                padding: 8px;
                padding-left: 20px;
                border: 1px solid #D1D5DB;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
        """)
        self.year_dropdown.addItem("All Years")
        self.year_dropdown.addItems([str(year) for year in self.mobil.get_unique_years()])
        self.year_dropdown.currentIndexChanged.connect(self.showMobil)
        top_bar.addWidget(self.year_dropdown)

        top_bar.addStretch()

        main_layout.addLayout(top_bar)

        # Grid layout for car cards
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(5, 5, 5, 5)  # Set margins for the grid layout
        self.grid_layout.setSpacing(45)  # Set spacing between items in the grid layout
        main_layout.addLayout(self.grid_layout)

        # Load cars from database
        self.showMobil()

        # Pagination and bottom controls
        bottom_layout = self.setup_bottom_controls()
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)
        main_layout.addWidget(bottom_widget)  # Use addWidget instead of addLayout

    def create_card(self, image_data, title, color, license_plate, year, status_icon):
        """Create a card widget."""
        card_widget = QWidget()
        card_widget.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px;
                padding: 3px;
            }
        """)

        card_widget.setFixedSize(360, 340)  # Set a fixed width and height
        layout = QVBoxLayout(card_widget)

        # Add a drop shadow effect
        shadow_effect = QGraphicsDropShadowEffect(card_widget)
        shadow_effect.setBlurRadius(20)
        shadow_effect.setOffset(0, 5)
        shadow_effect.setColor(Qt.gray)
        card_widget.setGraphicsEffect(shadow_effect)

        # Car image
        car_image = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        pixmap = pixmap.scaled(335, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # Create a mask for rounded corners at the top
        mask = QPixmap(pixmap.size())
        mask.fill(Qt.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(Qt.NoPen)
        rect = QRect(0, 0, pixmap.width(), pixmap.height())
        painter.drawRoundedRect(rect, 20, 20)
        painter.end()
        
        pixmap.setMask(mask.createMaskFromColor(Qt.transparent, Qt.MaskInColor))
        car_image.setPixmap(pixmap)
        car_image.setAlignment(Qt.AlignLeft)
        car_image.setFixedSize(345, 200)  # Ensure the image fills the label
        layout.addWidget(car_image)

        # Edit button
        edit_button = QPushButton("Edit")
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                border: none;
                color: white;
                font-size: 14px;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        edit_button.setFixedSize(60, 30)
        edit_button.setParent(card_widget)
        edit_button.move(card_widget.width() - edit_button.width() - 10, 10)

        # Checkbox
        checkbox = QCheckBox()
        checkbox.setParent(card_widget)
        checkbox.move(10, 10)

        # Car information
        title_label = QLabel(title)
        title_label.setFont(QFont("Poly", 17, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        color_label = QLabel(color)
        color_label.setFont(QFont("Poly", 14))
        color_label.setWordWrap(True)
        color_label.setAlignment(Qt.AlignLeft)

        license_label = QLabel(license_plate)
        license_label.setFont(QFont("Poly", 14))
        license_label.setWordWrap(True)
        license_label.setAlignment(Qt.AlignLeft)

        year_label = QLabel(str(year))
        year_label.setFont(QFont("Poly", 14))
        year_label.setAlignment(Qt.AlignRight)

        # Info layout
        info_layout = QVBoxLayout()
        info_layout.addWidget(color_label)
        info_layout.addWidget(license_label)

        # Bottom row with year and status
        sec_info_layout = QVBoxLayout()
        sec_info_layout.addWidget(year_label)

        # Add status icon
        status_label = QLabel()
        status_icon_path = "./src/Component/checkbox_t.png" if status_icon == 1 else "./src/Component/checkbox.png"
        status_pixmap = QPixmap(status_icon_path).scaled(QSize(24, 24), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        status_label.setPixmap(status_pixmap)
        status_label.setAlignment(Qt.AlignRight)
        sec_info_layout.addWidget(status_label)

        bottom_layout = QHBoxLayout()
        bottom_layout.addLayout(info_layout)
        bottom_layout.addStretch()
        bottom_layout.addLayout(sec_info_layout)

        layout.addLayout(bottom_layout)

        return card_widget

    def showMobil(self, page=1):
        """Show cars from the database and display them."""
        # Clear the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        color = self.color_dropdown.currentText()
        year = self.year_dropdown.currentText()

        if color == "All Colors":
            color = None
        if year == "All Years":
            year = None
        else:
            try:
                year = int(year)
            except ValueError:
                year = None

        cars, total_records = self.mobil.get_mobil(page, self.items_per_page)
        
        if not cars:
            # Show message if no cars are available
            no_data_label = QLabel("Data Mobil tidak ada saat ini")
            no_data_label.setFont(QFont("Poly", 16, QFont.Bold))
            no_data_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(no_data_label, 0, 0, 1, 3)  # Span across 3 columns
            return

        for i in range(self.items_per_page):
            if i < len(cars):
                car = cars[i]
                card = self.create_card(
                    car['Gambar'],
                    car['Model'],
                    car['Warna'],
                    car['NomorPlat'],
                    car['Tahun'],
                    car['StatusKetersediaan']
                )
            else:
                # Create an empty widget for empty slots
                card = QWidget()
            self.grid_layout.addWidget(card, i // 3, i % 3)

        self.setup_pagination(total_records)

    def setup_pagination(self, total_records):
        """Set up pagination with a fixed window of 5 pages plus First/Last buttons."""
        # Create container widget
        pagination_container = QWidget()
        pagination_container.setFixedHeight(50)  # Set a fixed height for the pagination container
        pagination_layout = QHBoxLayout(pagination_container)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(8)
        
        # Add stretchable spacers on both sides of the pagination buttons
        pagination_layout.addStretch()

        # Calculate total pages
        self.total_pages = (total_records + self.items_per_page - 1) // self.items_per_page
        
        # Style for all pagination buttons
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
        
        # Clear existing buttons
        self.pagination_buttons = []
        
        # Create navigation buttons
        self.first_button = QPushButton("First")
        self.prev_button = QPushButton("←")
        self.next_button = QPushButton("→")
        self.last_button = QPushButton("Last")
        
        for btn in [self.first_button, self.prev_button, self.next_button, self.last_button]:
            btn.setStyleSheet(button_style)
        
        # Add First and Prev buttons
        pagination_layout.addWidget(self.first_button)
        pagination_layout.addWidget(self.prev_button)
        
        # Calculate the range of pages to display (sliding window of 5)
        def calculate_page_range():
            n = 5  # Number of page buttons to show
            if self.total_pages <= n:
                # If total pages is less than window size, show all pages
                start_page = 1
                end_page = self.total_pages
            else:
                # Calculate the start page based on current page
                start_page = max(1, min(self.current_page - n//2, self.total_pages - n + 1))
                end_page = start_page + n - 1
                
                # Adjust if we're near the end
                if end_page > self.total_pages:
                    end_page = self.total_pages
                    start_page = max(1, end_page - n + 1)
            
            return range(start_page, end_page + 1)
        
        # Add page buttons
        for page in calculate_page_range():
            btn = QPushButton(str(page))
            btn.setStyleSheet(button_style)
            if page == self.current_page:
                btn.setProperty("current", "true")
                btn.setStyleSheet(button_style + "font-weight: bold;")
            btn.setProperty("page_number", page)
            btn.clicked.connect(lambda checked, p=page: self.go_to_page(p))
            self.pagination_buttons.append(btn)
            pagination_layout.addWidget(btn)
        
        # Add Next and Last buttons
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addWidget(self.last_button)
        
        # Add stretchable spacers on both sides of the pagination buttons
        pagination_layout.addStretch()
        
        # Connect navigation button signals
        self.first_button.clicked.connect(lambda: self.go_to_page(1))
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        self.last_button.clicked.connect(lambda: self.go_to_page(self.total_pages))
        
        # Update button states
        self.update_pagination_buttons()
        
        return pagination_container

    def update_pagination_buttons(self):
        """Update the enabled state of all pagination buttons."""
        if all([self.first_button, self.prev_button, self.next_button, self.last_button]):
            # Disable First/Prev buttons if on first page
            self.first_button.setEnabled(self.current_page > 1)
            self.prev_button.setEnabled(self.current_page > 1)
            
            # Disable Next/Last buttons if on last page
            self.next_button.setEnabled(self.current_page < self.total_pages)
            self.last_button.setEnabled(self.current_page < self.total_pages)

        # Update the style of pagination buttons to reflect the current page
        for btn in self.pagination_buttons:
            if btn.property("page_number") == self.current_page:
                btn.setStyleSheet(btn.styleSheet() + "font-weight: bold;")
            else:
                btn.setStyleSheet(btn.styleSheet().replace("font-weight: bold;", ""))

    def go_to_page(self, page):
        """Navigate to a specific page number."""
        if 1 <= page <= self.total_pages and page != self.current_page:
            self.current_page = page
            self.showMobil(page)
            self.update_pagination_buttons()

    def prev_page(self):
        """Navigate to the previous page."""
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)

    def next_page(self):
        """Navigate to the next page."""
        if self.current_page < self.total_pages:
            self.go_to_page(self.current_page + 1)

    def add_mobil(self):
        """Add a new Mobil object."""
        dialog, data = MobilUI.formMobil(self, mode="create")
        
        if dialog and data:
            try:
                mobil = {
                    'NomorPlat': data['NomorPlat'],
                    'Gambar': data['Gambar'],
                    'Model': data['Model'],
                    'Warna': data['Warna'],
                    'Tahun': data['Tahun'],
                    'StatusKetersediaan': data['StatusKetersediaan']
                }
                self.mobil.set_mobil(mobil, mode="create")
                self.showMobil()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error adding car: {str(e)}")

    def delete_mobil(self):
        """Delete selected Mobil objects."""
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QMessageBox.warning(self, "Warning", "Please select at least one car to delete.")
            return
        
        if MobilUI.confirmMobil(self, len(selected_ids)):
            try:
                for car_id in selected_ids:
                    self.mobil.set_mobil({'NomorPlat': car_id}, mode="delete")
                self.showMobil()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting cars: {str(e)}")

    def get_selected_ids(self):
        """Get the IDs of selected cars."""
        selected_ids = []
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                checkbox = widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    label = widget.findChild(QLabel, "license_label")
                    if label:
                        selected_ids.append(label.text())
        return selected_ids

    def apply_filters(self):
        """Apply filters based on the selected color and year."""
        self.showMobil()

    def setup_bottom_controls(self):
        """Create and configure the bottom control panel."""
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
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if widget is not None:
                    checkbox = widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(not checkbox.isChecked())
        
        select_all_btn.clicked.connect(toggle_select_all)
        
        # Create pagination container
        pagination_container = self.setup_pagination(0)  # Initial setup with 0 total records
        
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
        add_button.clicked.connect(self.add_mobil)
        delete_button.clicked.connect(self.delete_mobil)
        
        # Assemble bottom layout
        bottom_layout.addWidget(select_all_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(pagination_container)
        bottom_layout.addStretch()
        bottom_layout.addWidget(add_button)
        bottom_layout.addSpacing(10)
        bottom_layout.addWidget(delete_button)
        
        return bottom_layout