import sys
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication, QMainWindow, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QStackedWidget, QPushButton
from PyQt5.QtGui import QFont, QIcon, QFontDatabase, QPixmap
from PyQt5.QtCore import Qt
from Mobil.MobilUI import MobilUI

class MenuUI(QMainWindow):
    def __init__(self):
        super(MenuUI, self).__init__()

        # Set Up Font Poly
        QFontDatabase.addApplicationFont("./src/Component/Poly/Poly-Regular.ttf")
        
        self.setWindowTitle("CarGoOwner")
        self.setGeometry(100, 100, 1512, 982)
        self.setStyleSheet("background-color : #FFFFFF")
        
        # Main container widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout
        main_layout = QHBoxLayout(main_widget) 
        
        # Create stacked widget
        self.stackedWidget = QStackedWidget()
        # Panggil Menu UI
        self.menu = self.MainUI()
        # Panggil Mobil UI
        self.mobil = MobilUI()
        # Panggil Peminjaman UI
        self.peminjaman = QWidget()
        # Panggil Pelanggan UI
        self.pelanggan = QWidget()
        # Panggil Jadwal Pengembalian UI
        self.jadwalpengembalian = QWidget()
        # Panggil Pembayaran Rental UI
        self.pembayaranrental = QWidget()
        # Panggil Histori Peminjaman Mobil UI
        self.historipeminjamanmobil = QWidget()
        # Panggil Status Ketersediaan Mobil UI
        self.statusketersediaanmobil = QWidget()
        # Panggil Pendapatan UI
        self.pendapatan = QWidget()

        self.stackedWidget.addWidget(self.menu)
        self.stackedWidget.addWidget(self.mobil)
        self.stackedWidget.addWidget(self.peminjaman)
        self.stackedWidget.addWidget(self.pelanggan)
        self.stackedWidget.addWidget(self.jadwalpengembalian)
        self.stackedWidget.addWidget(self.pembayaranrental)
        self.stackedWidget.addWidget(self.historipeminjamanmobil)
        self.stackedWidget.addWidget(self.statusketersediaanmobil)
        self.stackedWidget.addWidget(self.pendapatan)

        # Panggil sidebar dan separator
        sidebar, separator = self.create_sidebar()

        # Tambah sidebar and separator ke main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(separator)
        main_layout.addWidget(self.stackedWidget)
        self.stackedWidget.setCurrentWidget(self.menu)

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
            ("Mobil", "./src/Component/MobilIcon.png", [], self.onClickMobil),      
            ("Pelanggan", "./src/Component/PelangganIcon.png", [], self.onClickPelanggan),
            ("Peminjaman", "./src/Component/PeminjamanIcon.png", [], self.onClickPeminjaman),
            ("Notifikasi", "./src/Component/NotifikasiIcon.png", self.ShowNotifDropDown(), 0),
            ("Laporan", "./src/Component/LaporanIcon.png", self.ShowLaporanDropDown(), 0)
        ]

        for text, icon_path, submenus, function in menu_items:
            if not submenus:
                # Create a main button if no submenus exist
                item = QTreeWidgetItem([f"  {text}"])
                item.setFont(0, QFont("Poly", 13))
                item.setIcon(0, QIcon(icon_path))
                sidebar_tree.addTopLevelItem(item)

                # Handle click function
                if function:
                    sidebar_tree.itemClicked.connect(
                        lambda current_item, _, func=function, label=text: 
                        func() if current_item.text(0).strip() == label else None
                    )
            else:
                # Create a dropdown if submenus exist
                parent_item = QTreeWidgetItem([f"  {text}"])
                parent_item.setFont(0, QFont("Poly", 13))
                parent_item.setIcon(0, QIcon(icon_path))
                sidebar_tree.addTopLevelItem(parent_item)

                for submenu_text, func in submenus:
                    submenu_item = QTreeWidgetItem([f"    {submenu_text}"])
                    submenu_item.setFont(0, QFont("Poly", 12))
                    parent_item.addChild(submenu_item)
                    
                    # Handle submenu click
                    sidebar_tree.itemClicked.connect(
                        lambda current_item, _, func=func, label=submenu_text: 
                        func() if current_item.text(0).strip() == label else None
                    )
        sidebar_tree.itemClicked.connect(self.handle_item_click)

        # Nama Aplikasi
        app_name = QLabel("CarGoOwner.")
        app_name.setFont(QFont("Poly", 27))
        app_name.setStyleSheet("padding : 17px")

        # Widget sidebar
        sidebar_layout.addWidget(app_name)
        sidebar_layout.addWidget(sidebar_tree)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Separator
        separator = QLabel()
        separator.setStyleSheet("background-color: #414041;")
        separator.setFixedWidth(8)

        return sidebar_widget, separator 

    def handle_item_click(self, item):
        if item.childCount() > 0:
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)

    def ShowNotifDropDown(self):
        return [["Jadwal Pengembalian", self.onClickJadwalPengembalian], ["Pembayaran Rental", self.onClickPembayaranRental]]

    def ShowLaporanDropDown(self):
        return [["Status Ketersediaan Mobil", self.onClickStatusKetersediaanMobil], ["Histori Peminjaman Mobil", self.onClickHistoriPeminjamanMobil], ["Pendapatan", self.onClickPendapatan]]
  
    def onClickMobil(self):
        self.stackedWidget.setCurrentWidget(self.mobil)

    def onClickPeminjaman(self):
        self.stackedWidget.setCurrentWidget(self.peminjaman)

    def onClickPelanggan(self):
        self.stackedWidget.setCurrentWidget(self.pelanggan)
  
    def onClickJadwalPengembalian(self):
        self.stackedWidget.setCurrentWidget(self.jadwalpengembalian)

    def onClickPembayaranRental(self):
        self.stackedWidget.setCurrentWidget(self.pembayaranrental)
  
    def onClickStatusKetersediaanMobil(self):
        self.stackedWidget.setCurrentWidget(self.statusketersediaanmobil)
    
    def onClickHistoriPeminjamanMobil(self):
        self.stackedWidget.setCurrentWidget(self.historipeminjamanmobil)

    def onClickPendapatan(self):
        self.stackedWidget.setCurrentWidget(self.pendapatan)
        
    def MainUI(self):
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
        welcome_label.setFont(QFont("Poly", 22))

        wrapper_layout.addWidget(logo)
        wrapper_layout.addWidget(welcome_label)
        wrapper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align the entire wrapper at the top
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(logo_message_wrapper)

        return content_widget

def main():
    app = QApplication(sys.argv)
    window = MenuUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()