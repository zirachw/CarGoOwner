import sys
import MenuUI.MenuUI as MenuUI
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication, QMainWindow, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon, QFontDatabase


class MainWindowQMain(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set Up Font Poly
        QFontDatabase.addApplicationFont("./src/Component/Poly/Poly-Regular.ttf")
        
        self.setWindowTitle("CarGoOwner")
        self.setGeometry(100, 100, 1512, 982)
        self.setStyleSheet("background-color : #FFFFFF")
        
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

        menu = MenuUI.MenuUI()
        main_content = menu.MainUI()

        main_layout.addWidget(main_content) 
        main_layout.setStretch(2, 1)
        


    def create_sidebar(self):
        # Sidebar widget
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar_widget)

        # Sidebar tree
        sidebar_tree = QTreeWidget()
        sidebar_tree.setHeaderHidden(True)
        sidebar_tree.setExpandsOnDoubleClick(False)
        sidebar_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #FFFFFF;
                border: none;
                font-size: 14px;
            }
            QTreeWidget::item {
                background-color: #ffffff;
                margin: 1.5px;
                padding: 13px;
                border-radius: 10px; /* Rounded edges */
                color: #333333;
            }
            QTreeWidget::item:hover {
                background-color: #e0e0e0; 
                color: #000000; /* Change text color on hover */
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings  {
                border-image: none;
                image: none;
            }
        """)

        menu_items = [
            ("Mobil", "./src/Component/MobilIcon.png", []),      
            ("Pelanggan", "./src/Component/PelangganIcon.png", []),
            ("Peminjaman", "./src/Component/PeminjamanIcon.png", []),
            ("Notifikasi", "./src/Component/NotifikasiIcon.png", [("Jadwal Pengembalian"), ("Pembayaran Rental")]),
            ("Laporan", "./src/Component/LaporanIcon.png", [("Status Ketersediaan Mobil"), ("Histori Peminjaman Mobil"), ("Pendapatan")])
        ]

        for text, icon_path, submenus in menu_items:
            item = QTreeWidgetItem([f"  {text}"])
            item.setFont(0, QFont("Poly", 12))
            item.setIcon(0, QIcon(icon_path))
            sidebar_tree.addTopLevelItem(item)
            
            for submenu_text in submenus:
                submenu_item = QTreeWidgetItem([f"  {submenu_text}"])
                submenu_item.setFont(0, QFont("Poly", 12))
                item.addChild(submenu_item)

        # Connect the itemClicked signal to a slot
        sidebar_tree.itemClicked.connect(self.handle_item_click)

        # Nama Aplikasi
        app_name = QLabel("CarGoOwner.")
        app_name.setFont(QFont("Poly", 21))
        app_name.setStyleSheet("padding : 10px")

        # Widget sidebar
        sidebar_layout.addWidget(app_name)
        sidebar_layout.addWidget(sidebar_tree)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Separator
        separator = QLabel()
        separator.setStyleSheet("background-color: #414041;")
        separator.setFixedWidth(8)

        return sidebar_widget, separator  # Return both the sidebar widget and separator

    def handle_item_click(self, item):
        if item.childCount() > 0:
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)



def main():
    app = QApplication(sys.argv)
    window = MainWindowQMain()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()