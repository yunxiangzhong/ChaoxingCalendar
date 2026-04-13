import sys
import os
import re

# 导入crawl.py和ui.py的功能
from crawl import crawl_tasks
from ui import generate_html

# 主函数
def main():
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 处理自定义协议调用
        arg = sys.argv[1]
        if arg.startswith('cxcalendar://'):
            # 解析协议参数
            action = re.search(r'cxcalendar://(\w+)', arg)
            if action and action.group(1) == 'run':
                print(">>> 接收到同步命令，开始爬取学习通任务...")
                tasks = crawl_tasks()
                print(f">>> 爬取完成，共获取 {len(tasks)} 个任务")
                generate_html(tasks)
                return
    
    # 正常启动流程
    print(">>> 正在启动学习通任务管理...")
    print(">>> 首次运行，开始爬取学习通任务...")
    tasks = crawl_tasks()
    print(f">>> 爬取完成，共获取 {len(tasks)} 个任务")
    generate_html(tasks)

if __name__ == "__main__":
    main()
