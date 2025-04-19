from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap, QPen, QColor

class MapCanvas(QGraphicsView):
    def __init__(self, map_path):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 加载地图底图
        self.map_pixmap = QGraphicsPixmapItem(QPixmap(map_path))
        self.scene.addItem(self.map_pixmap)
        
        # 初始化绘制参数
        self.start_point = None
        self.end_point = None
        self.path_lines = []
        
        # 设置点击事件
        self.setMouseTracking(True)
        self.click_enabled = True

    def mousePressEvent(self, event):
        if self.click_enabled and event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())
            if not self.start_point:
                self.start_point = pos
                self.draw_point(pos, Qt.blue)
            else:
                self.end_point = pos
                self.draw_point(pos, Qt.red)
                self.request_path_calculation()

    def draw_point(self, pos, color):
        self.scene.addEllipse(pos.x()-5, pos.y()-5, 10, 10, 
                            QPen(color, 2), Qt.SolidPattern)

    def draw_path(self, path_coords):
        # 清除旧路径
        for line in self.path_lines:
            self.scene.removeItem(line)
        
        # 绘制新路径
        pen = QPen(QColor(255, 0, 0), 3)
        for i in range(len(path_coords)-1):
            start = path_coords[i]
            end = path_coords[i+1]
            line = self.scene.addLine(start.x(), start.y(), end.x(), end.y(), pen)
            self.path_lines.append(line)

    def request_path_calculation(self):
        self.click_enabled = False
        start_node = self.convert_to_graph_coord(self.start_point)
        end_node = self.convert_to_graph_coord(self.end_point)

        # 用 Q-learning 计算路径
        from algorithms.q_learning import calculate_path
        path_points = [QPointF(x, y) for (x, y) in calculate_path(start_node, end_node)]
        self.draw_path(path_points)
        self.reset_selection()

    def convert_to_graph_coord(self, ui_point):
        """将界面坐标转换为图数据坐标"""
        # 需要根据你的地图实际比例实现
        return (int(ui_point.x()/10), int(ui_point.y()/10))  # 示例比例

    

    def convert_to_ui_coord(self, graph_point):
        """将图数据坐标转换为界面坐标"""
        return QPointF(graph_point[0]*10, graph_point[1]*10)  # 示例比例

    def reset_selection(self):
        self.start_point = None
        self.end_point = None
        self.click_enabled = True