
# 文件：gui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox)
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
        
        # 起点输入
        lbl_start = QLabel("起点ID:")
        self.txt_start = QLineEdit()
        self.txt_start.setFixedWidth(100)
        
        # 终点输入
        lbl_end = QLabel("终点ID:")
        self.txt_end = QLineEdit()
        self.txt_end.setFixedWidth(100)
        
        # 确认按钮
        btn_confirm = QPushButton("开始规划")
        btn_confirm.clicked.connect(self._handle_planning)
        btn_confirm.setStyleSheet("background-color: #4CAF50; color: white;")
        
        # 组装面板
        panel.addWidget(lbl_start)
        panel.addWidget(self.txt_start)
        panel.addWidget(lbl_end)
        panel.addWidget(self.txt_end)
        panel.addWidget(btn_confirm)
        panel.addStretch(1)
        
        return panel
    
    def _handle_planning(self):
        """处理规划按钮点击"""
        # 获取输入值
        start_id = self.txt_start.text().strip()
        end_id = self.txt_end.text().strip()
        
        # 输入验证
        if not start_id or not end_id:
            QMessageBox.warning(self, "输入错误", "请输入完整的起点和终点ID")
            return
            
        try:
            start_id = int(start_id)
            end_id = int(end_id)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "ID必须为数字")
            return
            
        # 验证节点存在性
        if start_id not in self.path_service.nodes:
            QMessageBox.warning(self, "节点错误", f"起点ID {start_id} 不存在")
            return
            
        if end_id not in self.path_service.nodes:
            QMessageBox.warning(self, "节点错误", f"终点ID {end_id} 不存在")
            return
            
        # 触发路径计算
        self.map_canvas.start_path_planning(start_id, end_id)