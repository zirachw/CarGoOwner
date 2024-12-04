import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap, QIcon, QFontDatabase
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set Up Font Poly
        QFontDatabase.addApplicationFont("./src/Component/Poly/Poly-Regular.ttf")

        # Set the window title and dimensions
        self.setWindowTitle("CarGoOwner")
        self.setGeometry(100, 100, 1512, 982)
        self.setStyleSheet("background-color : #FFFFFF")
        self.MainUI()
        
    def MainUI(self):
        # Main container widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layouts
        main_layout = QHBoxLayout(main_widget) 
        
        # Panggil sidebar dan separator
        sidebar, separator = self.create_sidebar()

        # Tambah sidebar and separator ke main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(separator)

        # Main content
        content_widget = QWidget()  
        content_layout = QVBoxLayout(content_widget)

        logo_message_wrapper = QWidget()
        wrapper_layout = QVBoxLayout(logo_message_wrapper)

        logo = QLabel()
        LogoImg = QPixmap("./src/Component/Logo.png")
        scaled_logo = LogoImg.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(scaled_logo)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_label = QLabel("Welcome Back, Salsabiila!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Poly", 18))

        wrapper_layout.addWidget(logo)
        wrapper_layout.addWidget(welcome_label)
        wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align the entire wrapper at the top
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(logo_message_wrapper)

        main_layout.addWidget(content_widget) 
        main_layout.setStretch(2, 1)

    def create_sidebar(self):
        # Sidebar widget
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar_widget)

        # Sidebar list
        sidebar_list = QListWidget()
        sidebar_list.setSpacing(1)
        sidebar_list.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                background-color: #ffffff;
                margin: 1.5px;
                padding: 10px;
                border-radius: 10px; /* Rounded edges */
                color: #333333;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0; /* Lighter background on hover */
                color: #000000; /* Change text color on hover */
            }
        """)

        # Add icons and labels to the sidebar
        menu_items = [
            ("Mobil", "./src/Component/MobilIcon.png"),       # Replace with your custom icon path
            ("Pelanggan", "./src/Component/PelangganIcon.png"),
            ("Peminjaman", "./src/Component/PeminjamanIcon.png"),
            ("Notifikasi", "./src/Component/NotifikasiIcon.png"),
            ("Laporan", "./src/Component/LaporanIcon.png")
        ]
        for text, icon_path in menu_items:
            item = QListWidgetItem(f"  {text}")  # Add some spacing for aesthetics
            item.setIcon(QIcon(icon_path))       # Set the custom icon
            sidebar_list.addItem(item)
        
        # App name label
        app_name = QLabel("CarGoOwner.")
        app_name.setFont(QFont("Poly", 19))
        app_name.setStyleSheet("padding : 10px")

        # Add widgets to the sidebar layout
        sidebar_layout.addWidget(app_name)
        sidebar_layout.addWidget(sidebar_list)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Separator
        separator = QLabel()
        separator.setStyleSheet("background-color: #414041;")
        separator.setFixedWidth(8)

        return sidebar_widget, separator  # Return both the sidebar widget and separator
        



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()