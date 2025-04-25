from PyQt5.QtCore import QObject, pyqtSignal
from .q_learning import (
    read_node_data, 
    read_edge_data, 
    q_learning, 
    extract_path
)
import math

class PathService(QObject):
    path_calculated = pyqtSignal(list)
    calculation_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.nodes = None
        self.graph = None
        self.original_costs = {}  # 用来保存边的原始代价
        self.station_ids = [4, 23, 11, 46, 32, 52]

    def initialize_data(self, node_file: str, edge_file: str):
        """初始化节点和边数据"""
        try:
            self.nodes = read_node_data(node_file)
            self.graph = read_edge_data(edge_file, self.nodes)
            if not self.nodes or not self.graph:
                raise ValueError("数据文件内容为空")
        except Exception as e:
            raise RuntimeError(f"数据加载失败：{str(e)}")

    def calculate_path(self, start_id: int, end_id: int):
        """执行路径计算"""
        try:
            Q = q_learning(self.graph, start_id, end_id)
            path_ids = extract_path(Q, start_id, end_id)

            # 计算路径总长度
            total_length = 0.0
            for i in range(len(path_ids) - 1):
                total_length += self.graph[path_ids[i]][path_ids[i + 1]]

            # 打印结果
            print("\n计算完成的最优路径:")
            print(" -> ".join(map(str, path_ids)))
            print(f"路径总长度: {total_length:.2f}")

            path_coords = [self.nodes[node_id] for node_id in path_ids]
            self.path_calculated.emit(path_coords)
            print("路径计算完成！", "path_coords:", path_coords)
            print("path_ids:", path_ids)
            # 返回路径坐标列表，交给地图组件显示
            return path_coords

        except Exception as e:
            self.calculation_failed.emit(str(e))

    import math

    def find_nearest_station(self, start_id: int) -> int:
        """
        使用经纬度坐标计算欧几里得距离寻找最近充电站
        （基于 read_node_data() 返回的 {id: (lat, lon)} 格式）
        """
        if not self.nodes or start_id not in self.nodes:
            raise ValueError("起点ID不存在或节点数据未加载")

        # 获取起点经纬度
        start_lat, start_lon = self.nodes[start_id]
        min_distance = float('inf')
        nearest_station_id = None

        for station_id in self.station_ids:
            try:
                # 获取充电站经纬度
                station_lat, station_lon = self.nodes[station_id]

                # 计算简化版欧几里得距离（经纬度差值）
                distance = math.sqrt((station_lat - start_lat) ** 2 +
                                     (station_lon - start_lon) ** 2)


                if distance < min_distance:
                    min_distance = distance
                    nearest_station_id = station_id

            except KeyError:
                print(f"⚠️ 忽略缺失坐标的充电站: {station_id}")
            except Exception as e:
                print(f"⚠️ 计算站 {station_id} 距离时出错: {str(e)}")

        if nearest_station_id is None:
            raise RuntimeError("所有充电站均不可用")

        print(f"最近充电站: {station_id} (校准距离: {min_distance:.6f})")
        return nearest_station_id

    def apply_penalty_area(self, center: tuple, radius: float, penalty_factor: float = 1000.0):
        """
        对落在指定圆形区域内的路径增加代价。
        :param center: (x, y) 圆心坐标
        :param radius: 圆半径
        :param penalty_factor: 惩罚倍数，默认为 1000 倍
        """
        if self.nodes is None or self.graph is None:
            print("图数据未初始化，无法应用惩罚区域。")
            return

        cx, cy = center
        for u in self.graph:
            for v in self.graph[u]:
                if v not in self.nodes or u not in self.nodes:
                    continue
                x1, y1 = self.nodes[u]
                x2, y2 = self.nodes[v]
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                dist_sq = (mx - cx) ** 2 + (my - cy) ** 2
                if dist_sq <= radius ** 2:
                    # 如果这条边尚未保存过原始代价，保存原始代价
                    if (u, v) not in self.original_costs:
                        self.original_costs[(u, v)] = self.graph[u][v]

                    # 应用惩罚
                    original_cost = self.graph[u][v]
                    self.graph[u][v] = original_cost * penalty_factor
                    print(f"边 ({u}, {v}) 位于惩罚区域内，代价从 {original_cost} 增加到 {self.graph[u][v]}")

    def reset_penalty(self):
        """重置惩罚并恢复所有边的原始代价"""
        if self.original_costs:
            for (u, v), original_cost in self.original_costs.items():
                self.graph[u][v] = original_cost  # 恢复原始代价
                print(f"恢复边 ({u}, {v}) 的代价为 {original_cost}")
            # 清空原始代价字典
            self.original_costs.clear()
