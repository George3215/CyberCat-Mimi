import subprocess

def get_active_window_info():
    """
    使用 AppleScript 获取 macOS 当前活动窗口的应用名称和窗口标题。
    
    返回示例: "Visual Studio Code (main.py — cat_mimi)"
    """
    try:
        # 获取最前端进程名称
        cmd_app = "osascript -e 'tell application \"System Events\" to get name of first process whose frontmost is true'"
        app_name = subprocess.check_output(cmd_app, shell=True).decode().strip()
        
        # 获取该进程的当前窗口标题
        cmd_title = f"osascript -e 'tell application \"System Events\" to tell (first process whose frontmost is true) to get name of window 1'"
        window_title = subprocess.check_output(cmd_title, shell=True).decode().strip()
        
        return f"{app_name} ({window_title})"
    except Exception as e:
        # 如果获取失败（如某些 App 不支持或没有窗口），则只返回应用名或 Unknown
        try:
            return app_name
        except:
            return "Unknown"

if __name__ == "__main__":
    # 简单的测试逻辑
    print(f"当前活动窗口: {get_active_window_info()}")
