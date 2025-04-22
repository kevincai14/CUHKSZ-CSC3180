
# 文件：gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from gui.map_canvas import MapCanvas

from PyQt5.QtWidgets import QTextEdit

class MainWindow(QMainWindow):
    def __init__(self, map_path: str, path_service):
        super().__init__()
        self.path_service = path_service
        self._init_ui(map_path)

    def _init_ui(self, map_path: str):
        self.setWindowTitle("智能路径规划系统")
        self.resize(1200, 800)

        # 创建地图组件
        self.map_canvas = MapCanvas(map_path)
        self.map_canvas.path_service = self.path_service

        # 创建信息面板
        self.info_panel = QTextEdit()
        self.info_panel.setReadOnly(True)
        self.info_panel.setFixedWidth(300)
        # self.info_panel.setStyleSheet("background-color: #f0f0f0;")
        self.info_panel.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 8px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 20px;
                color: #333333;
            }
        """)

        # 将 info_panel 传给 map_canvas
        self.map_canvas.set_info_panel(self.info_panel)

        # 控制面板（顶部按钮）
        control_panel = self._create_control_panel()

        # 左侧垂直布局：按钮 + 地图
        left_layout = QVBoxLayout()
        left_layout.addLayout(control_panel, stretch=0)
        left_layout.addWidget(self.map_canvas, stretch=1)

        # 主水平布局：左侧地图区域 + 右侧信息面板
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=4)
        main_layout.addWidget(self.info_panel, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _create_control_panel(self):
        """创建顶部控制面板"""
        panel = QHBoxLayout()

        # 重置按钮
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self._handle_reset)
        btn_reset.setStyleSheet("background-color: #FF5722; color: white;")

        # 车祸按钮
        btn_carcrash = QPushButton("Simulate Car Crash")
        btn_carcrash.clicked.connect(self._car_crash)
        btn_carcrash.setStyleSheet("background-color: #FF5722; color: white;")

        # 暴雨按钮
        btn_rainstorm = QPushButton("Simulate Rainstorm")
        btn_rainstorm.clicked.connect(self._trigger_rainstorm)
        btn_rainstorm.setStyleSheet("background-color: #FF5722; color: white;")

        # 组装面板
        panel.addWidget(btn_reset)
        panel.addWidget(btn_carcrash)
        panel.addWidget(btn_rainstorm)
        panel.addStretch(1)

        return panel

    def _handle_reset(self):
        """处理重置按钮点击"""
        self.map_canvas.reset_selection()

        self.info_panel.clear()  # 清除信息面板的内容

    def _car_crash(self):
        """处理重置按钮点击"""
        self.map_canvas.add_simulated_carcrash()
        
    def _trigger_rainstorm(self):
        """处理重置按钮点击"""
        self.map_canvas.add_simulated_carcrash()
