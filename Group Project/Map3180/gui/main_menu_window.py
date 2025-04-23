# gui/main_menu_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class MainMenuWindow(QMainWindow):
    def __init__(self, start_callback):
        super().__init__()
        self.setWindowTitle("路径规划系统")
        self.resize(800, 600)
        self.start_callback = start_callback  # 正确保存回调函数
        self._init_ui()

    def _init_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # 开始按钮
        start_btn = QPushButton("开 始")
        start_btn.setFixedSize(200, 60)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 24px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        start_btn.clicked.connect(self.start_callback)  # 直接使用回调

        # 布局设置
        main_layout.addWidget(start_btn)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)