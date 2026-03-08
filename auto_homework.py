import sys
import os
import time
import traceback

from crawl import crawl_tasks
from ui import generate_html

# 获取当前脚本路径
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 40)
    print(">>> 学习通任务管理系统")
    print("=" * 40)
    
    # 爬取任务
    print(">>> 开始爬取学习通任务...")
    tasks = crawl_tasks()
    
    # 生成HTML
    print("-" * 40)
    print(">>> 抓取完成，正在生成任务管理系统...")
    html_path = generate_html(tasks)
    
    print("-" * 40)
    print(">>> 程序已完成，3秒后自动退出...")
    time.sleep(3)
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 输出详细的错误信息到文件
        error_log = os.path.join(base_path, "error.log")
        with open(error_log, "w", encoding="utf-8") as f:
            f.write(f"Error type: {type(e).__name__}\n")
            f.write(f"Error message: {e}\n")
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
        # 显示错误信息
        input(f"程序执行出错！详细信息已保存到 {error_log}\n错误信息: {e}\n按回车键退出...")
