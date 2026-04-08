import sys
from PyQt6.QtWidgets import QApplication
from cat import DesktopCat

def main():
    """
    CyberCat-Mimi 项目启动入口。
    
    本项目是一个基于 PyQt6 的桌面宠物，集成了 Ollama 本地大模型。
    通过异步线程进行决策，实现了状态驱动的行为系统与智能对话气泡。
    """
    app = QApplication(sys.argv)
    
    # 允许主窗口关闭时不立即退出程序（防止气泡等子窗口异常导致崩溃）
    app.setImplicitExit(True)
    
    # 初始化主窗口
    cat = DesktopCat()
    
    # 运行事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
