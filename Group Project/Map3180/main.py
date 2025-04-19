
# 文件：main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from algorithms.path_service import PathService
from PyQt5.QtWidgets import QMessageBox

def resource_path(relative_path):
    """资源路径处理（兼容开发模式和打包模式）"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def initialize_services():
    """初始化核心服务"""
    # 配置数据文件路径
    config = {
        'node_file': resource_path('data/node_py_data.txt'),
        'edge_file': resource_path('data/edge_py_data.txt'),
        'map_image': resource_path('data/map_image.png')
    }
    
    try:
        # 初始化路径计算服务
        path_service = PathService()
        path_service.initialize_data(
            config['node_file'], 
            config['edge_file']
        )
        # 验证至少存在2个节点
        if len(path_service.nodes) < 2:
            raise ValueError("节点数据不足，至少需要2个节点")
        
        return config, path_service
    except Exception as e:
        QMessageBox.critical(
            None, 
            "初始化失败", 
            f"服务初始化失败：{str(e)}\n"
            f"请检查数据文件是否存在：\n"
            f"节点文件：{config['node_file']}\n"
            f"边文件：{config['edge_file']}"
        )
        sys.exit(1)

if __name__ == "__main__":
    # 应用初始化
    app = QApplication(sys.argv)
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 初始化服务
    config, path_service = initialize_services()
    
    try:
        # 创建主窗口并注入服务
        window = MainWindow(
            map_path=config['map_image'],
            path_service=path_service
        )
        window.setWindowTitle("智能路径规划系统")
        window.show()
        
        # 启动事件循环
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(
            None, 
            "运行时错误", 
            f"应用程序意外终止：{str(e)}"
        )
        sys.exit(1)
