import sys
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication, QMainWindow, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QStackedWidget, QPushButton, QDesktopWidget
from PyQt5.QtGui import QFont, QIcon, QFontDatabase, QPixmap
from PyQt5.QtCore import Qt
from Mobil.MobilUI import MobilUI
from Peminjaman.peminjamanUI import PeminjamanUI

class MenuUI(QMainWindow):
    def __init__(self):
        super(MenuUI, self).__init__()

        # Set Up Font Poly
        QFontDatabase.addApplicationFont("./src/Component/Poly/Poly-Regular.ttf")
        
        self.setWindowTitle("CarGoOwner")
        self.screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, self.screen.width(), self.screen.height())  
        self.setMinimumSize(self.screen.width(), self.screen.height()) 
        self.setStyleSheet("background-color : #FFFFFF")
        self.sidebar_width = int(self.screen.width() * 0.2)
        
        # Main container widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout
        main_layout = QHBoxLayout(main_widget) 
        main_layout.setSpacing(0)  # Remove spacing between widgets
        
        # Create stacked widget
        self.stackedWidget = QStackedWidget()
        # Initialize all UI components
        self.menu = self.MainUI()
        self.mobil = MobilUI()
        # Panggil Peminjaman UI
        self.peminjaman = PeminjamanUI(schema_path="schema.sql")
        # Panggil Pelanggan UI
        self.pelanggan = QWidget()
        self.jadwalpengembalian = QWidget()
        self.pembayaranrental = QWidget()
        self.historipeminjamanmobil = QWidget()
        self.statusketersediaanmobil = QWidget()
        self.pendapatan = QWidget()

        # Add widgets to stacked widget
        self.stackedWidget.addWidget(self.menu)
        self.stackedWidget.addWidget(self.mobil)
        self.stackedWidget.addWidget(self.peminjaman)
        self.stackedWidget.addWidget(self.pelanggan)
        self.stackedWidget.addWidget(self.jadwalpengembalian)
        self.stackedWidget.addWidget(self.pembayaranrental)
        self.stackedWidget.addWidget(self.historipeminjamanmobil)
        self.stackedWidget.addWidget(self.statusketersediaanmobil)
        self.stackedWidget.addWidget(self.pendapatan)

        # Create sidebar and separator
        sidebar, separator = self.create_sidebar()

        # Add widgets to main layout with specific ratios
        main_layout.addWidget(sidebar)
        main_layout.addWidget(separator)
        main_layout.addWidget(self.stackedWidget)
        
        # Set the current widget and maximize window
        self.stackedWidget.setCurrentWidget(self.menu)
        self.setWindowState(Qt.WindowMaximized)

        # Set stretch factors for layout (1:0:4 ratio)
        main_layout.setStretch(0, 1)  # Sidebar takes 1 part
        main_layout.setStretch(1, 0)  # Separator takes minimal space
        main_layout.setStretch(2, 4)  # Main content takes 4 parts
        
    def create_sidebar(self):
        # Sidebar widget
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(self.sidebar_width)  # Reduced width
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 30, 0, 0)  # Add top margin of 30px

        # Nama Aplikasi
        app_name = QLabel("CarGoOwner.")
        app_name.setFont(QFont("Poly", 27))
        app_name.setStyleSheet("padding: 17px; margin-bottom: 20px;")  # Added bottom margin

        # Sidebar tree
        sidebar_tree = QTreeWidget()
        sidebar_tree.setHeaderHidden(True)
        sidebar_tree.setFixedWidth(self.sidebar_width)
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
                border-radius: 10px;
                color: #333333;
            }
            QTreeWidget::item:hover {
                background-color: #e0e0e0; 
                color: #000000;
                padding :10px;
                border-radius: 10px;
            }
            QTreeWidget::item:selected {
                background-color: #e0e0e0;
                outline: none;
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

        # Menu items setup
        menu_items = [
            ("Mobil", "./src/Component/MobilIcon.png", [], self.onClickMobil),      
            ("Pelanggan", "./src/Component/PelangganIcon.png", [], self.onClickPelanggan),
            ("Peminjaman", "./src/Component/PeminjamanIcon.png", [], self.onClickPeminjaman),
            ("Notifikasi", "./src/Component/NotifikasiIcon.png", self.ShowNotifDropDown(), 0),
            ("Laporan", "./src/Component/LaporanIcon.png", self.ShowLaporanDropDown(), 0)
        ]

        for text, icon_path, submenus, function in menu_items:
            if not submenus:
                item = QTreeWidgetItem([f"  {text}"])
                item.setFont(0, QFont("Poly", 13))
                item.setIcon(0, QIcon(icon_path))
                sidebar_tree.addTopLevelItem(item)

                if function:
                    sidebar_tree.itemClicked.connect(
                        lambda current_item, _, func=function, label=text: 
                        func() if current_item.text(0).strip() == label else None
                    )
            else:
                parent_item = QTreeWidgetItem([f"  {text}"])
                parent_item.setFont(0, QFont("Poly", 13))
                parent_item.setIcon(0, QIcon(icon_path))
                sidebar_tree.addTopLevelItem(parent_item)

                for submenu_text, func in submenus:
                    submenu_item = QTreeWidgetItem([f"    {submenu_text}"])
                    submenu_item.setFont(0, QFont("Poly", 12))
                    parent_item.addChild(submenu_item)
                    
                    sidebar_tree.itemClicked.connect(
                        lambda current_item, _, func=func, label=submenu_text: 
                        func() if current_item.text(0).strip() == label else None
                    )
        
        sidebar_tree.itemClicked.connect(self.handle_item_click)

        # Add widgets to sidebar layout
        sidebar_layout.addWidget(app_name)
        sidebar_layout.addWidget(sidebar_tree)

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
        return [["Status Ketersediaan", self.onClickStatusKetersediaanMobil], ["Histori Peminjaman", self.onClickHistoriPeminjamanMobil], ["Pendapatan", self.onClickPendapatan]]
  
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