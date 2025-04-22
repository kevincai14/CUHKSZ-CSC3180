
from PyQt5.QtCore import Qt, QPointF, QThreadPool, QRunnable
from PyQt5.QtGui import QPixmap, QPen, QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QMessageBox, QGraphicsEllipseItem, QGraphicsLineItem
)
from algorithms.path_service import PathService
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal

class PathSignals(QObject):
    finished = pyqtSignal(list)

class PathWorker(QRunnable):
    finished = pyqtSignal(list)
    def __init__(self, service: PathService, start_id: int, end_id: int):
        super().__init__()
        self.signals = PathSignals()  # 信号封装在QObject中
        self.service = service
        self.start_id = start_id
        self.end_id = end_id
        self.path_coords = []
        

    def run(self) -> None:
        """执行路径计算任务"""
        self.path_coords = self.service.calculate_path(self.start_id, self.end_id)
        self.signals.finished.emit(self.path_coords)  # 通过QObject发射信号

    def get_path_coords(self) -> list:
        return self.path_coords


class MapCanvas(QGraphicsView):
    def __init__(self, map_path: str):
        super().__init__()
        # 初始化场景和地图
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.map_pixmap = QGraphicsPixmapItem(QPixmap(map_path))
        self.scene.addItem(self.map_pixmap)

        # 初始化路径服务
        self.path_service = PathService()
        self.thread_pool = QThreadPool.globalInstance()

        # 初始化状态变量
        self.start_id: int | None = None
        self.end_id: int | None = None
        self.path_lines = []
        self.click_enabled = True
        self.highlighted_node = None
        self.highlighted_marker = None

        # 连接信号槽
        self.path_service.calculation_failed.connect(self._show_error)
        self.path_service.path_calculated.connect(self._draw_path)  # 新增连接

        # 设置交互属性
        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        print("MapCanvas initialized!")


    # -------------------- 核心交互方法 --------------------
    def mousePressEvent(self, event) -> None:
        """鼠标点击事件处理"""
        if self.click_enabled and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            closest_id = self._get_closest_node(scene_pos)
            print(
                f"原始点击坐标：{event.pos().x()},{event.pos().y()} → 场景坐标：{scene_pos.x():.1f},{scene_pos.y():.1f}")

            if closest_id:
                if not self.start_id:
                    self._handle_start_selection(closest_id, scene_pos)
                else:
                    self._handle_end_selection(closest_id, scene_pos)

    def mouseMoveEvent(self, event) -> None:
        """鼠标移动事件处理"""
        if self.click_enabled:
            scene_pos = self.mapToScene(event.pos())
            closest_id = self._get_closest_node(scene_pos)

            if closest_id:
                if self.highlighted_node != closest_id:
                    if self.highlighted_marker:
                        self.scene.removeItem(self.highlighted_marker)
                    self.highlighted_node = closest_id
                    self.highlighted_marker = self._draw_highlighted_node(closest_id)
            else:
                if self.highlighted_marker:
                    self.scene.removeItem(self.highlighted_marker)
                    self.highlighted_node = None
                    self.highlighted_marker = None

    def _draw_highlighted_node(self, node_id: int):
        """绘制高亮节点标记"""
        x, y = self.path_service.nodes[node_id]
        marker = QGraphicsEllipseItem(x - 8, y - 8, 16, 16)
        marker.setPen(QPen(QColor(0, 255, 0), 2))  # 绿色高亮
        marker.setBrush(QBrush(QColor(0, 255, 0, 100)))  # 半透明绿色填充
        self.scene.addItem(marker)
        return marker

    def _handle_start_selection(self, node_id: int, pos: QPointF) -> None:
        """处理起点选择"""
        self.start_id = node_id
        self._draw_node_marker(node_id, Qt.blue)
        print(f"起点选择: 节点{node_id} @ ({pos.x():.1f}, {pos.y():.1f})")

    def _handle_end_selection(self, node_id: int, pos: QPointF) -> None:
        """处理终点选择"""
        self.end_id = node_id
        self._draw_node_marker(node_id, Qt.red)
        print(f"终点选择: 节点{node_id} @ ({pos.x():.1f}, {pos.y():.1f})")
        self.path_lines = self._start_calculation()



    # -------------------- 路径计算相关 --------------------
    def _start_calculation(self) -> list:
        """启动后台计算任务"""
        self.set_loading_state(True)
        worker = PathWorker(self.path_service, self.start_id, self.end_id)

        worker.signals.finished.connect(self._on_path_calculated)  # 正确连接信号
        self.thread_pool.start(worker)

        path_coords = worker.get_path_coords()
        print("计算完成", "path__coords: ", path_coords)
        return path_coords

    def _on_path_calculated(self, path_coords: list):
        """处理计算结果"""
        self.set_loading_state(False)
        self._draw_path(path_coords)
        print(f"Path: {path_coords}")

    # -------------------- 图形绘制方法 --------------------
    def _draw_node_marker(self, node_id: int, color: Qt.GlobalColor) -> None:
        """绘制节点标记"""
        print(
            f"绘制节点{node_id} @ ({self.path_service.nodes[node_id][0]:.1f}, {self.path_service.nodes[node_id][1]:.1f})")
        x, y = self.path_service.nodes[node_id]
        marker = QGraphicsEllipseItem(x - 8, y - 8, 16, 16)
        marker.setPen(QPen(color, 2))
        marker.setBrush(QBrush(color))
        self.scene.addItem(marker)

    def _draw_path(self, path_coords: list):
        """根据路径坐标绘制线条"""
        # 清除旧的路径线条
        print("绘制路径")
        for line in self.path_lines:
            self.scene.removeItem(line)
        self.path_lines = []

        # 绘制新的路径线条
        print("开始绘制路径", path_coords)
        for i in range(len(path_coords) - 1):
            start_x, start_y = path_coords[i]
            end_x, end_y = path_coords[i + 1]
            line = QGraphicsLineItem(start_x, start_y, end_x, end_y)
            line.setPen(QPen(QColor(255, 0, 0), 2))  # 红色线条
            self.scene.addItem(line)
            self.path_lines.append(line)
        print("路径绘制完成")

        self.set_loading_state(False)

    # -------------------- 辅助方法 --------------------
    def _get_closest_node(self, pos: QPointF) -> int | None:
        """获取最近节点ID（带阈值检测）"""
        min_dist = float('inf')
        closest_id = None
        for node_id, (x, y) in self.path_service.nodes.items():
            dist = (pos.x() - x) ** 2 + (pos.y() - y) ** 2
            if dist < min_dist and dist < 2500:  # 50像素阈值
                min_dist = dist
                closest_id = node_id
        return closest_id

    def set_loading_state(self, loading: bool) -> None:
        """更新加载状态"""
        self.click_enabled = not loading
        self.setCursor(Qt.WaitCursor if loading else Qt.ArrowCursor)

    def _show_error(self, msg: str) -> None:
        """显示错误信息"""
        self.set_loading_state(False)
        QMessageBox.critical(self, "路径计算错误", f"错误详情：\n{msg}")
        self.reset_selection()

    def start_path_planning(self, start_id: int, end_id: int):
        """通过编程方式启动路径规划"""
        # 清除旧选择
        self.reset_selection()

        # 绘制起点终点
        self._draw_node_marker(start_id, Qt.blue)
        self._draw_node_marker(end_id, Qt.red)

        # 启动计算
        self.start_id = start_id
        self.end_id = end_id
        self.path_lines = self._start_calculation()
        path_coords = self.path_lines.copy()
        print(f"路径规划结果: {path_coords}")
        # self._draw_path(path_coords)
        # print("start_planning函数完成")


    def reset_selection(self):
        """增强版重置方法"""
        self.start_id = None
        self.end_id = None
        self.click_enabled = True
        # 清除所有临时图形
        for item in self.scene.items():
            if isinstance(item, (QGraphicsEllipseItem, QGraphicsLineItem)):
                self.scene.removeItem(item)
        # 保留底图
        if not any(isinstance(item, QGraphicsPixmapItem) for item in self.scene.items()):
            self.scene.addItem(self.map_pixmap)
        # 清除路径线条列表
        self.path_lines = []


# -------------------- 测试代码 --------------------
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow


    def test_app():
        app = QApplication(sys.argv)
        window = QMainWindow()

        # 使用测试地图路径
        canvas = MapCanvas("data/test_map.jpg")
        window.setCentralWidget(canvas)
        window.resize(800, 600)
        window.show()

        sys.exit(app.exec_())


    test_app()
