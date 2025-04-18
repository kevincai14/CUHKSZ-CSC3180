import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
import os

def resource_path(relative_path):
    """ PyInstaller打包后获取资源的绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 加载地图资源
    map_image = resource_path("data/map_image.png")
    
    window = MainWindow(map_image)
    window.show()
    
    sys.exit(app.exec_())