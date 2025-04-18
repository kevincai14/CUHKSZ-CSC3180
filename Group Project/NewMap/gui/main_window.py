from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from .map_canvas import MapCanvas

class MainWindow(QMainWindow):
    def __init__(self, map_path):
        super().__init__()
        self.setWindowTitle("Path Finder")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建地图组件
        self.map_canvas = MapCanvas(map_path)
        
        # 布局设置
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.map_canvas)
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget)