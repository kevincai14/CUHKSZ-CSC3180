from PyQt5.QtCore import QObject, pyqtSignal
from .q_learning import (
    read_node_data, 
    read_edge_data, 
    q_learning, 
    extract_path
)

class PathService(QObject):
    path_calculated = pyqtSignal(list)
    calculation_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.nodes = None
        self.graph = None

    def initialize_data(self, node_file: str, edge_file: str):
        """初始化节点和边数据"""
        try:
            self.nodes = read_node_data(node_file)
            self.graph = read_edge_data(edge_file)
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
        except Exception as e:
            self.calculation_failed.emit(str(e))