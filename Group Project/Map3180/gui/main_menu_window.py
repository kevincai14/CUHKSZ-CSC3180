
# gui/main_menu_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QApplication)
from PyQt5.QtGui import (QPixmap, QPainter, QColor, QBrush, QPalette, QImage)
from PyQt5.QtCore import Qt

class MainMenuWindow(QMainWindow):
    def __init__(self, start_callback, map_path="data/map_image.png"):
        super().__init__()
        self.start_callback = start_callback
        self.map_path = map_path
        
        # 窗口初始化
        self.setWindowTitle("智能路径规划系统")
        self.resize(800, 600)
        
        # 初始化UI
        self._init_background()
        self._init_ui()

    def _init_background(self):
        """初始化静态模糊背景"""
        # 加载原始图片
        pixmap = QPixmap(self.map_path)
        # 缩放填充
        scaled_pix = pixmap.scaled(
            self.size(), 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        )
        
        # 应用模糊处理
        painter = QPainter(scaled_pix)
        for _ in range(8):  # 模糊强度
            painter.drawPixmap(0, 0, scaled_pix)
        painter.end()
        
        # 添加深色遮罩
        overlay = QImage(scaled_pix.size(), QImage.Format_ARGB32)
        overlay.fill(QColor(30, 30, 30, 180))
        
        painter.begin(scaled_pix)
        painter.drawImage(0, 0, overlay)
        painter.end()
        
        # 设置背景
        palette = self.palette()
        palette.setBrush(QPalette.Background, QBrush(scaled_pix))
        self.setPalette(palette)

    def _init_ui(self):
        """初始化界面组件"""
        # 主容器
        container = QWidget()
        container.setAttribute(Qt.WA_TranslucentBackground)
        
        # 按钮布局
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        # 开始按钮
        start_btn = QPushButton("START")
        start_btn.setFixedSize(240, 60)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 144, 255, 220);
                color: white;
                font-size: 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(70, 130, 180, 240);
            }
        """)
        start_btn.clicked.connect(self.start_callback)
        
        # 退出按钮
        exit_btn = QPushButton("EXIT") 
        exit_btn.setFixedSize(240, 60)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 50, 50, 220);
                color: white;
                font-size: 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(220, 70, 70, 240);
            }
        """)
        exit_btn.clicked.connect(QApplication.instance().quit)
        
        # 添加组件
        layout.addWidget(start_btn)
        layout.addWidget(exit_btn)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def resizeEvent(self, event):
        """窗口大小变化时刷新背景"""
        self._init_background()
        super().resizeEvent(event)
