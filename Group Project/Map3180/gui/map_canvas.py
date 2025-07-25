# gui/map_canvas.py

from PyQt5.QtCore import (
    Qt, QPointF, QThreadPool, QRunnable,
    QObject, pyqtSignal, QTimer  # 新增QTimer
)
from PyQt5.QtGui import (
    QPixmap, QPen, QBrush, QColor,
    QFont, QPainter, QPainterPath,  # 新增QPainterPath
)
from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QMessageBox, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsPathItem,  QTextEdit            # 新增阴影效果
)
from algorithms.path_service import PathService
from math import atan2, degrees

var_special_mode_active = 0

class PathSignals(QObject):
    finished = pyqtSignal(list)

class PathWorker(QRunnable):
    def __init__(self, service: PathService, start_id: int, end_id: int):
        super().__init__()
        self.signals = PathSignals()
        self.service = service
        self.start_id = start_id
        self.end_id = end_id
        self.path_coords = []

    def run(self) -> None:
        """执行路径计算任务"""
        self.path_coords = self.service.calculate_path(self.start_id, self.end_id)
        self.signals.finished.emit(self.path_coords)

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

        self.info_panel = None
        # 初始化车祸标记
        self.accident_icon = QPixmap("data/car_crash.png")  # 确保图片路径正确
        self.accident_marker = None 
        
        # 初始化暴雨标记
        self.rain_icon = QPixmap("data/rain_cloud.png")  # 使用半透明积雨云图片
        self.rain_marker = None
        self.temp_marker = None  # 新增临时标记
        self.current_rain_radius = 100  # 默认影响半径
        self.current_penalty_factor = 50.0  # 默认惩罚系数
        self.is_rain_active = False

        # 初始化充电站图标/id
        self.gas_icon = QPixmap("data/charge_station.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.gas_station_ids = [4, 23, 11, 46, 32, 52]
         # 新增箭头图标初始化
        self.start_icon = QPixmap("data/start_arrow.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.end_icon = QPixmap("data/end_arrow.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.hover_icon = QPixmap("data/hover_arrow.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # 新增标记对象
        self.hover_marker = None  # 鼠标悬停临时标记
        self.start_marker = None  # 正式起点标记
        self.end_marker = None 

        # 新增动画相关属性
        self.animation_offset = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        

        # 初始化路径服务
        self.path_service = PathService()
        self.thread_pool = QThreadPool.globalInstance()

        # 初始化状态变量
        self.start_id = None
        self.end_id = None
        self.path_lines = []
        self.click_enabled = True
        self.highlighted_node = None
        self.highlighted_marker = None
        self.path_completed = False  # 新增标志位

        # 连接信号槽
        self.path_service.calculation_failed.connect(self._show_error)
        self.path_service.path_calculated.connect(self._draw_path)

        # 设置交互属性
        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        print("MapCanvas initialized!")

    def set_info_panel(self, panel: QTextEdit):
        """设置右侧信息面板"""
        self.info_panel = panel

    # -------------------- 核心交互方法 --------------------
    def mousePressEvent(self, event) -> None:
        global var_special_mode_active

        # 如果路径已完成且不在特殊模式下，忽略点击
        if self.path_completed and var_special_mode_active == 0:
            return
        # 在特殊模式下禁用常规的起点终点选择
        if (var_special_mode_active == 0 or var_special_mode_active == 3) and self.click_enabled and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            print(f"Mouse clicked at: {scene_pos}")
            closest_id = self._get_closest_node(scene_pos)

            # 普通模式下的节点选择
            if closest_id:
                if not self.start_id:
                    self._handle_start_selection(closest_id, scene_pos)
                    if var_special_mode_active == 3:
                        nearest_id = self.path_service.find_nearest_station(closest_id)
                        self._handle_end_selection(nearest_id, scene_pos, True)
                elif not self.end_id:  # 只有在终点未设置时才处理
                    self._handle_end_selection(closest_id, scene_pos)

        # ================= 特殊模式处理 =================
        elif var_special_mode_active == 1 and event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            
            # 创建正式标记
            scaled_icon = self.rain_icon.scaled(
                int(self.current_rain_radius * 2),
                int(self.current_rain_radius * 2),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 应用透明度
            painter = QPainter(scaled_icon)
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.fillRect(scaled_icon.rect(), QColor(0, 0, 0, 150))
            painter.end()
            
            # 添加正式标记
            self.rain_marker = QGraphicsPixmapItem(scaled_icon)
            self.rain_marker.setOffset(-scaled_icon.width()/2, -scaled_icon.height()/2)
            self.rain_marker.setPos(scene_pos)
            self.scene.addItem(self.rain_marker)
            
            # 应用最终参数
            self.path_service.apply_penalty_area(
                (scene_pos.x(), scene_pos.y()),
                radius=self.current_rain_radius,
                penalty_factor=self.current_penalty_factor
            )
            
            # 退出特殊模式并重置
            var_special_mode_active = 0
            self._clear_temp_markers()
            self.current_rain_radius = 100  # 重置默认值
            self.current_penalty_factor = 50.0
            
            # 更新信息面板
            if self.info_panel:
                self.info_panel.append(f"⛈️ Rainstorm is placed（radius：{self.current_rain_radius}px）")
            
            event.accept()
            return


        # 车祸模式（var_special_mode_active == 2）
        elif var_special_mode_active == 2:
            scene_pos = self.mapToScene(event.pos())

            # 创建高可见度车祸标记
            scaled_icon = self.accident_icon.scaled(150, 150,
                                                    Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.SmoothTransformation
                                                    )

            # 添加标记到场景（无需透明）
            self.accident_marker = QGraphicsPixmapItem(scaled_icon)
            self.accident_marker.setOffset(-scaled_icon.width() / 2, -scaled_icon.height() / 2)
            self.accident_marker.setPos(scene_pos)
            self.scene.addItem(self.accident_marker)

            # 应用强路径惩罚（完全避让）
            self.path_service.apply_penalty_area(
                (scene_pos.x(), scene_pos.y()),
                radius=25,
                penalty_factor=1000.0
            )
            var_special_mode_active = 0  # 退出特殊模式

    def mouseMoveEvent(self, event):
        if self.click_enabled:
            scene_pos = self.mapToScene(event.pos())
            closest_id = self._get_closest_node(scene_pos)
            # ...原有高亮逻辑保持不变...
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

        # 暴雨模式移动效果
        if var_special_mode_active == 1:
            self._clear_temp_markers()
            scene_pos = self.mapToScene(event.pos())
            
            if self.temp_marker:
                self.scene.removeItem(self.temp_marker)
            
            # 创建新尺寸图标
            scaled_icon = self.rain_icon.scaled(
                int(self.current_rain_radius * 2),
                int(self.current_rain_radius * 2),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 应用透明度
            painter = QPainter(scaled_icon)
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.fillRect(scaled_icon.rect(), QColor(0, 0, 0, 150))
            painter.end()
            
            # 创建新临时标记
            self.temp_marker = QGraphicsPixmapItem(scaled_icon)
            self.temp_marker.setOffset(-scaled_icon.width()/2, -scaled_icon.height()/2)
            self.temp_marker.setPos(scene_pos)
            self.scene.addItem(self.temp_marker)
        
        elif var_special_mode_active == 2:
            scene_pos = self.mapToScene(event.pos())
            x, y = scene_pos.x(), scene_pos.y()

            # 清除旧标记
            if self.accident_marker:
                self.scene.removeItem(self.accident_marker)

            # 创建新标记
            scaled_icon = self.accident_icon.scaled(
                150, 150, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.accident_marker = QGraphicsPixmapItem(scaled_icon)
            self.accident_marker.setOffset(
                -scaled_icon.width() / 2, 
                -scaled_icon.height() / 2
            )
            self.accident_marker.setPos(x, y)
            self.scene.addItem(self.accident_marker)

        elif var_special_mode_active == 3:

            # 加油/充电站模式：高亮所有充电站节点
            if not hasattr(self, 'station_markers_shown'):
                self.station_markers_shown = False  # 标记是否已经显示过充电站图标

            if not self.station_markers_shown:  # 只在第一次显示时执行
                if not hasattr(self, 'gas_markers'):
                    self.gas_markers = []
                # 若已有标记，清除
                for marker in self.gas_markers:
                    self.scene.removeItem(marker)
                self.gas_markers.clear()

                # 遍历所有充电站节点
                for node_id in self.gas_station_ids:
                    if node_id in self.path_service.nodes:
                        x, y = self.path_service.nodes[node_id]
                        # 创建充电站图标（确保 self.gas_icon 已经加载）
                        gas_marker = QGraphicsPixmapItem(self.gas_icon)
                        gas_marker.setOffset(-self.gas_icon.width() / 2, -self.gas_icon.height())
                        gas_marker.setPos(x, y)
                        self.scene.addItem(gas_marker)

                        # 添加到标记列表
                        self.gas_markers.append(gas_marker)

                # 标记图标已显示过，防止重复更改
                self.station_markers_shown = True



    def wheelEvent(self, event):
        """鼠标滚轮事件处理（完全重构）"""
        global var_special_mode_active
        
        if var_special_mode_active == 1 and self.temp_marker:
            # 计算缩放步长
            delta = event.angleDelta().y() / 120
            scale_factor = 1.1 if delta > 0 else 0.9
            
            # 更新参数（限制范围）
            self.current_rain_radius = max(50, min(300, int(self.current_rain_radius * scale_factor)))
            self.current_penalty_factor = max(10.0, min(200.0, self.current_penalty_factor * scale_factor))
            
            # 强制刷新临时标记
            self.mouseMoveEvent(event)
            event.accept()
        else:
            super().wheelEvent(event)

    def _clear_temp_markers(self):
        """清除临时标记"""
        if self.temp_marker:
            self.scene.removeItem(self.temp_marker)
            self.temp_marker = None
        # 保留已确认的暴雨标记

    
    def _update_rain_marker(self):
        """更新暴雨标记显示"""
        if self.rain_marker:
            # 移除旧标记
            self.scene.removeItem(self.rain_marker)
            
            # 创建新尺寸图标
            scaled_icon = self.rain_icon.scaled(
                int(self.current_rain_radius * 2),  # 直径=半径*2
                int(self.current_rain_radius * 2),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 应用透明度
            painter = QPainter(scaled_icon)
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.fillRect(scaled_icon.rect(), QColor(0, 0, 0, 150))
            painter.end()
            
            # 重新创建标记
            self.rain_marker = QGraphicsPixmapItem(scaled_icon)
            self.rain_marker.setOffset(-scaled_icon.width()/2, -scaled_icon.height()/2)
            self.rain_marker.setPos(self.rain_marker.pos())  # 保持原位置
            self.scene.addItem(self.rain_marker)
    
    # ----------- 画节点 ---------------------- #
    def _draw_highlighted_node(self, node_id: int):
        """替换原有高亮逻辑为箭头图标"""
        # 移除旧的高亮标记
        if self.hover_marker:
            self.scene.removeItem(self.hover_marker)
        
        # 获取节点坐标
        x, y = self.path_service.nodes[node_id]
        
        # 创建半透明悬停标记
        transparent_icon = self.hover_icon.copy()
        painter = QPainter(transparent_icon)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(transparent_icon.rect(), QColor(0,0,0,128))  # 50%透明度
        painter.end()
        
        # 添加新标记
        self.hover_marker = QGraphicsPixmapItem(transparent_icon)
        self.hover_marker.setOffset(-transparent_icon.width()/2, -transparent_icon.height())  # 居中显示
        self.hover_marker.setPos(x, y)
        self.scene.addItem(self.hover_marker)
        return self.hover_marker

    def _handle_start_selection(self, node_id: int, pos: QPointF) -> None:
        """处理起点选择（新增图标）"""
        # 移除旧标记
        if self.start_marker:
            self.scene.removeItem(self.start_marker)
        
        self.start_id = node_id
        # 创建新标记
        x, y = self.path_service.nodes[node_id]
        self.start_marker = QGraphicsPixmapItem(self.start_icon)
        self.start_marker.setOffset(-self.start_icon.width()/2, -self.start_icon.height())
        self.start_marker.setPos(x, y)
        self.scene.addItem(self.start_marker)
        print(f"起点选择: 节点{node_id} @ ({pos.x():.1f}, {pos.y():.1f})")
    
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
    
    def _handle_end_selection(self, node_id: int, pos: QPointF, mode = False) -> None:
        """处理终点选择（新增图标）"""
        # 移除旧标记
        if self.end_marker:
            self.scene.removeItem(self.end_marker)

        self.end_id = node_id
        # 创建新标记
        x, y = self.path_service.nodes[node_id]
        self.end_marker = QGraphicsPixmapItem(self.end_icon)
        self.end_marker.setOffset(-self.end_icon.width() / 2, -self.end_icon.height())
        self.end_marker.setPos(x, y)
        if mode == False:
            self.scene.addItem(self.end_marker)


        print(f"终点选择: 节点{node_id} @ ({pos.x():.1f}, {pos.y():.1f})")
        self.path_lines = self._start_calculation()
        self.path_completed = True  # 设置路径完成标志

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
        """路径绘制函数（带完善的自然语言导航）"""
        # 清除旧路径元素
        for item in self.path_lines:
            self.scene.removeItem(item)
        self.path_lines = []
        self.animation_offset = 0

        # 绘制路径（原有代码保留）
        if len(path_coords) >= 2:
            path = QPainterPath()
            path.moveTo(*path_coords[0])
            for coord in path_coords[1:]:
                path.lineTo(*coord)
            
            path_item = QGraphicsPathItem(path)
            pen = QPen(QColor(30, 144, 255), 4)
            pen.setDashPattern([10, 5])
            pen.setCapStyle(Qt.RoundCap)
            pen.setDashOffset(self.animation_offset)
            path_item.setPen(pen)
            
            self.scene.addItem(path_item)
            self.path_lines.append(path_item)
            self.animation_timer.start(50)

        # 生成导航指引
        if self.info_panel and self.path_service and len(path_coords) >= 2:
            directions = []
            current_dir = None
            current_length = 0.0
            total_length = 0.0

            # 方向箭头映射表
            DIRECTION_ARROWS = {
                "north": "↑",
                "northeast": "↗",
                "east": "→",
                "southeast": "↘",
                "south": "↓",
                "southwest": "↙",
                "west": "←",
                "northwest": "↖",
                "ahead": "▲"
            }

            # 直接处理所有路径段（包含起点到第一个节点）
            for i in range(len(path_coords)-1):
                start = path_coords[i]
                end = path_coords[i+1]
                
                # 获取实际路径长度（千米单位）
                segment_length = self._get_segment_length(start, end)
                
                # 计算方向
                direction = self._get_direction(start, end)
                print(f"Segment Length: {segment_length:.3f} km. Direction: {direction}")

                # 格式化方向显示
                arrow = DIRECTION_ARROWS.get(direction.lower(), "➤")
                colored_dir = f'<font color="red">{direction.capitalize()}</font> {arrow}'
                
                # 合并连续相同方向
                if direction == current_dir:
                    current_length += segment_length
                    directions[-1] = f"{colored_dir} for {current_length:.3f}km"

                else:                
                    # 方向不相同    
                    current_dir = direction
                    current_length = segment_length
                    if current_dir is not None:
                        directions.append(f"{colored_dir} for {current_length:.3f}km")
                    else:# 第一次方向
                        directions.append(f"{colored_dir} for {segment_length:.3f}km")
                    current_dir = direction
                    
                total_length += segment_length

            print(directions)

            # 构建指引文本
            instruction_html = "<b>🚀 Navigation Guidance:</b><br>"
            steps = ["Start from departure point:"]
            for i, d in enumerate(directions):
                j = i + 1
                steps.append(f"{j}. Go {d}")
            steps.append(f"Arrive at destination!")
            
            instruction_html += "<br>".join(steps)

            # 添加统计信息
            instruction_html += f"<br><br><b>📊 Journey Summary:</b>"
            instruction_html += f"<br>• Total distance: {total_length:.2f}km"
            instruction_html += f"<br>• Number of segments: {len(directions)}"

            self.info_panel.setHtml(instruction_html)

        self.set_loading_state(False)

    def _get_segment_length(self, start, end):
        """获取实际路径长度（千米单位）"""
        # 查找最近节点
        start_node = min(self.path_service.nodes.items(), 
                        key=lambda item: (item[1][0]-start[0])**2 + (item[1][1]-start[1])**2)
        end_node = min(self.path_service.nodes.items(),
                    key=lambda item: (item[1][0]-end[0])**2 + (item[1][1]-end[1])**2)
        
        # 从图数据获取实际长度（单位：千米）
        return self.path_service.graph[start_node[0]].get(end_node[0], 0.0)

    def _get_direction(self, start, end):
        """Calculate direction with precise node coordinates"""
        dx = end[0] - start[0]
        dy = start[1] - end[1]  # Inverted y-axis
        
        # Handle straight directions
        if dx == 0:
            return "north" if dy > 0 else "south"
        if dy == 0:
            return "east" if dx > 0 else "west"
        
        angle = degrees(atan2(dy, dx))
        
        # Detailed direction thresholds
        if -12.5 <= angle < 12.5:
            return "east"
        elif 12.5 <= angle < 77.5:
            return "northeast"
        elif 77.5 <= angle < 102.5:
            return "north"
        elif 102.5 <= angle < 167.5:
            return "northwest"
        elif angle >= 167.5 or angle < -167.5:
            return "west"
        elif -167.5 <= angle < -102.5:
            return "southwest"
        elif -102.5 <= angle < -77.5:
            return "south"
        elif -77.5 <= angle < -12.5:
            return "southeast"

    def _update_animation(self):
        """更新动画帧"""
        # 虚线流动
        self.animation_offset = (self.animation_offset - 2) % 15
        for item in self.path_lines:
            if isinstance(item, QGraphicsPathItem):
                pen = item.pen()
                pen.setDashOffset(self.animation_offset)
                item.setPen(pen)

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
        QMessageBox.critical(self, "Calculation Error", f"Details:\n{msg}")
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

    def add_simulated_rainstorm(self):
        """启用暴雨模式"""
        global var_special_mode_active
        var_special_mode_active = 1
        self.click_enabled = True


    def reset_selection(self):
        """增强版重置方法"""
        self.start_id = None
        self.end_id = None
        self.path_completed = False  # 重置完成标志
        self.click_enabled = True
        global var_special_mode_active
        var_special_mode_active = 0

        # 停止动画
        self.animation_timer.stop()

        """重置时清除所有箭头标记"""
        # 新增清除起点、终点箭头逻辑
        for marker in [self.hover_marker, self.start_marker, self.end_marker]:
            if marker:
                self.scene.removeItem(marker)
        self.hover_marker = None
        self.start_marker = None
        self.end_marker = None

        # 清除所有临时图形，包括车祸图标, 暴雨图标, 路径线条
        for item in self.scene.items():
            if isinstance(item, (QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPixmapItem)):
                self.scene.removeItem(item)
        # 保留底图
        if not any(isinstance(item, QGraphicsPixmapItem) for item in self.scene.items()):
            self.scene.addItem(self.map_pixmap)
        # 清除路径线条列表
        self.path_lines = []

        # 清空信息面板
        if hasattr(self, 'info_panel'):
            self.info_panel.clear()

        self.path_service.reset_penalty()
        self.station_markers_shown = False

    def add_simulated_carcrash(self):
        """放置车祸点位"""
        #设置车祸模式
        global var_special_mode_active
        var_special_mode_active = 2
        self.click_enabled = True

    def add_simulated_station(self):
        """进入找加油站模式"""
        #设置找加油站模式
        global var_special_mode_active
        var_special_mode_active = 3
        self.click_enabled = True
