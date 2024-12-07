from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QWidget 
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class MenuUI(QMainWindow):
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