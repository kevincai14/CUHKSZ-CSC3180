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
        # 窗口基础设置
        self.setWindowTitle("AI-Based Navigation System")
        self.resize(1800, 1800)
        self.setStyleSheet("background-color: #F5F5F5;")

        # 地图组件初始化
        self.map_canvas = MapCanvas(map_path)
        self.map_canvas.path_service = self.path_service

        # 信息面板样式优化
        self.info_panel = QTextEdit()
        self.info_panel.setReadOnly(True)
        self.info_panel.setFixedWidth(475)
        self.info_panel.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 2px solid #2196F3;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Palatino Linotype';
                font-size: 30px;
                color: #333333;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        """)

        # 组件关联
        self.map_canvas.set_info_panel(self.info_panel)

        # 布局构建
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # 左侧布局（地图+控制面板）
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addLayout(self._create_control_panel())
        left_layout.addWidget(self.map_canvas)
        
        # 组合主界面
        main_layout.addWidget(left_widget, 4)
        main_layout.addWidget(self.info_panel, 1)
        self.setCentralWidget(main_widget)

    def _create_control_panel(self):
        """创建顶部控制面板（优化版）"""
        panel = QHBoxLayout()
        panel.setContentsMargins(10, 10, 10, 10)
        panel.setSpacing(15)

        # 推荐尺寸200x60，带透明通道
        # button_style = """
        #     QPushButton {
        #         border-image: url(data/button_bg.png) 0 0 0 0 stretch stretch;  # 核心修改
        #         color: #FFFFFF;
        #         /* 保留其他样式 */
        #     }
        #     QPushButton:hover {
        #         border-image: url(data/button_hover_bg.png);  # 悬停状态图片
        #         background-color: rgba(25, 118, 210, 0.5);  # 叠加半透明颜色
        #     }
        # """

        # 统一按钮样式
        button_style = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                min-width: 120px;
                transition: all 0.3s;
            }
            QPushButton:hover {
                background-color: #1976D2;
                transform: translateY(-1px);
                box-shadow: 0 3px 6px rgba(0,0,0,0.16);
            }
            QPushButton:pressed {
                background-color: #1565C0;
                transform: translateY(0);
            }
        """

        # 重置按钮
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self._handle_reset)
        btn_reset.setStyleSheet("background-color: #FF5722; color: white;")

        # 交通事故按钮
        btn_crash = QPushButton("Simulate Crash")
        btn_crash.clicked.connect(self._car_crash)
        btn_crash.setStyleSheet(button_style)

        # 恶劣天气按钮
        btn_weather = QPushButton("Simulate Rainstorm")
        btn_weather.clicked.connect(self._trigger_rainstorm)
        btn_weather.setStyleSheet(button_style)

        # 最近加油站按钮
        btn_nearest_station = QPushButton("Find Nearest Fuel Station")
        btn_nearest_station.clicked.connect(self._find_nearest_station)
        btn_nearest_station.setStyleSheet(button_style)

        # 添加按钮和弹性空间
        panel.addWidget(btn_reset)
        panel.addWidget(btn_crash)
        panel.addWidget(btn_weather)
        panel.addWidget(btn_nearest_station)
        panel.addStretch(1)

        return panel

    def _handle_reset(self):
        """重置操作增强"""
        self.map_canvas.reset_selection()
        self.info_panel.clear()
        self.info_panel.setPlainText("System reset\nWaiting for new path planning...")

    def _car_crash(self):
        """交通事故模拟"""
        self.map_canvas.add_simulated_carcrash()
        self.info_panel.append("⚠️ Traffic accident simulation activated")

    def _trigger_rainstorm(self):
        """恶劣天气模拟"""
        self.map_canvas.add_simulated_rainstorm()
        self.info_panel.append("⛈️ Rainstorm simulation activated")

    def _find_nearest_station(self):
        """寻找最近加油/充电站"""
        self.map_canvas.add_simulated_station()
        self.info_panel.append("Nearest charging station search mode activated")

