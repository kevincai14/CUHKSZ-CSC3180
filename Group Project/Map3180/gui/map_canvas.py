# 文件：map_canvas.py
from PyQt5.QtCore import Qt, QPointF, QThreadPool, QRunnable
from PyQt5.QtGui import QPixmap, QPen, QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QMessageBox, QGraphicsEllipseItem, QGraphicsLineItem
)
from algorithms.path_service import PathService


class PathWorker(QRunnable):
    def __init__(self, service: PathService, start_id: int, end_id: int):
        super().__init__()
        self.service = service
        self.start_id = start_id
        self.end_id = end_id

    def run(self) -> None:
        """执行路径计算任务"""
        self.service.calculate_path(self.start_id, self.end_id)


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
        self.direct_connection = None

        # 连接信号槽
        self.path_service.path_calculated.connect(self._on_path_calculated)
        self.path_service.calculation_failed.connect(self._show_error)

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
            print(f"原始点击坐标：{event.pos().x()},{event.pos().y()} → 场景坐标：{scene_pos.x():.1f},{scene_pos.y():.1f}")

            if closest_id:
                if not self.start_id:
                    self._handle_start_selection(closest_id, scene_pos)
                else:
                    self._handle_end_selection(closest_id, scene_pos)

    def mouseMoveEvent(self, event) -> None:
        """鼠标移动事件处理"""
        scene_pos = self.mapToScene(event.pos())
        closest_id = self._get_closest_node(scene_pos)

        # 移除之前高亮的节点
        if self.highlighted_node:
            self.scene.removeItem(self.highlighted_node)
            self.highlighted_node = None

        # 如果有附近的节点，高亮显示
        if closest_id:
            x, y = self.path_service.nodes[closest_id]
            highlight_pen = QPen(QColor(0, 255, 0), 4)  # 绿色高亮
            highlight_brush = QBrush(QColor(0, 255, 0, 100))  # 半透明绿色
            self.highlighted_node = QGraphicsEllipseItem(x - 12, y - 12, 24, 24)
            self.highlighted_node.setPen(highlight_pen)
            self.highlighted_node.setBrush(highlight_brush)
            self.scene.addItem(self.highlighted_node)

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
        self._start_calculation()
        self._draw_direct_connection()

    # -------------------- 路径计算相关 --------------------
    def _start_calculation(self) -> None:
        """启动后台计算任务"""
        self.set_loading_state(True)
        worker = PathWorker(self.path_service, self.start_id, self.end_id)
        self.thread_pool.start(worker)

    def _on_path_calculated(self, path_coords: list) -> None:
        """处理计算结果"""
        self.set_loading_state(False)
        self._draw_path([QPointF(x, y) for x, y in path_coords])
        self.reset_selection()

    # -------------------- 图形绘制方法 --------------------
    def _draw_node_marker(self, node_id: int, color: Qt.GlobalColor) -> None:
        """绘制节点标记"""
        print(f"绘制节点{node_id} @ ({self.path_service.nodes[node_id][0]:.1f}, {self.path_service.nodes[node_id][1]:.1f})")
        x, y = self.path_service.nodes[node_id]
        marker = QGraphicsEllipseItem(x - 8, y - 8, 16, 16)
        marker.setPen(QPen(color, 2))
        marker.setBrush(QBrush(color))
        self.scene.addItem(marker)

    def _draw_path(self, path_points: list) -> None:
        """绘制路径（带动画效果）"""
        # 清除旧路径
        for item in self.path_lines:
            self.scene.removeItem(item)

        # 绘制新路径
        path_pen = QPen(QColor(255, 165, 0), 4)  # 橙色路径
        for i in range(len(path_points) - 1):
            line = self.scene.addLine(
                path_points[i].x(), path_points[i].y(),
                path_points[i + 1].x(), path_points[i + 1].y(),
                path_pen
            )
            self.path_lines.append(line)

    def _draw_direct_connection(self):
        """绘制起点和终点之间的直接连接"""
        if self.start_id and self.end_id and self.start_id in self.path_service.graph and self.end_id in self.path_service.graph[self.start_id]:
            start_x, start_y = self.path_service.nodes[self.start_id]
            end_x, end_y = self.path_service.nodes[self.end_id]
            pen = QPen(QColor(255, 0, 0), 2)  # 红色线条
            if self.direct_connection:
                self.scene.removeItem(self.direct_connection)
            self.direct_connection = self.scene.addLine(start_x, start_y, end_x, end_y, pen)

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
        self._start_calculation()
        self._draw_direct_connection()

    def reset_selection(self):
        """增强版重置方法"""
        self.start_id = None
        self.end_id = None
        self.click_enabled = True
        # 清除所有临时图形
        for item in self.scene.items():
            if isinstance(item, (QGraphicsEllipseItem, QGraphicsLineItem)):
                self.scene.removeItem(item)
        self.direct_connection = None
        # 保留底图
        if not any(isinstance(item, QGraphicsPixmapItem) for item in self.scene.items()):
            self.scene.addItem(self.map_pixmap)
        self.path_lines = []
        if self.highlighted_node:
            self.scene.removeItem(self.highlighted_node)
            self.highlighted_node = None


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