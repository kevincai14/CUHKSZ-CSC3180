
# 文件：gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from gui.map_canvas import MapCanvas


class MainWindow(QMainWindow):
    def __init__(self, map_path: str, path_service):
        super().__init__()
        self.path_service = path_service
        self._init_ui(map_path)

    def _init_ui(self, map_path: str):
        # 主窗口设置
        self.setWindowTitle("智能路径规划系统")
        self.resize(1200, 800)

        # 创建地图组件
        self.map_canvas = MapCanvas(map_path)
        self.map_canvas.path_service = self.path_service

        # 创建控制面板
        control_panel = self._create_control_panel()

        # 设置布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(control_panel, stretch=0)
        main_layout.addWidget(self.map_canvas, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _create_control_panel(self):
        """创建顶部控制面板"""
        panel = QHBoxLayout()

        # 重置按钮
        btn_reset = QPushButton("重置")
        btn_reset.clicked.connect(self._handle_reset)
        btn_reset.setStyleSheet("background-color: #FF5722; color: white;")

        # 组装面板
        panel.addWidget(btn_reset)
        panel.addStretch(1)

        return panel

    def _handle_reset(self):
        """处理重置按钮点击"""
        self.map_canvas.reset_selection()

