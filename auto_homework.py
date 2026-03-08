import sys
import os

import time
import re
import json
import datetime
import hashlib
import webbrowser

# 1. 强制 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options # 引入 Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 获取当前脚本路径
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# 使用本地 Edge 驱动
driver_path = os.path.join(base_path, "msedgedriver.exe")
if os.path.exists(driver_path):
    SERVICE = Service(driver_path)
    print(f">>> 使用本地驱动: {driver_path}")
else:
    SERVICE = Service()
    print(">>> 使用系统默认驱动")

MAX_COURSES_COUNT = 4 

USERNAME = "xxxx" 
PASSWORD = "xxxx"
# ===========================================

# --- 辅助函数 ---
def register_protocol():
    import winreg
    import os
    protocol_name = "cxcalendar"
    try:
        # 获取当前可执行文件的完整路径
        if getattr(sys, 'frozen', False):
            # 打包后的exe文件
            exe_path = sys.executable
        else:
            # 开发环境下的python脚本
            # 协议应该指向最终的exe文件路径，而不是python脚本
            # 所以我们需要手动指定exe文件的路径
            base_path = os.path.dirname(os.path.abspath(__file__))
            exe_path = os.path.join(base_path, "dist", "auto_homework.exe")
        
        # 创建协议注册表项
        key_path = f"Software\\Classes\\{protocol_name}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f"URL:{protocol_name} Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
        
        # 创建shell\open\command项
        command_path = f"{key_path}\\shell\\open\\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_path) as key:
            # 确保路径使用双引号包围，处理包含空格的路径
            winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
        
        return True
    except Exception as e:
        return False

def generate_task_id(course, title, time_str):
    raw_str = f"{course}_{title}_{time_str}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()

def get_deadline_details(text):
    now = datetime.datetime.now()
    match_day = re.search(r"剩余(\d+)天", text)
    match_hour = re.search(r"剩余(\d+)小时", text)
    match_min = re.search(r"(\d+)分钟", text)
    target_dt = None
    if match_day:
        days = int(match_day.group(1))
        target_dt = now + datetime.timedelta(days=days)
        target_dt = target_dt.replace(hour=23, minute=59, second=59)
    elif match_hour:
        hours = int(match_hour.group(1))
        mins = int(match_min.group(1)) if match_min else 0
        target_dt = now + datetime.timedelta(hours=hours, minutes=mins)
    elif match_min:
        mins = int(match_min.group(1))
        target_dt = now + datetime.timedelta(minutes=mins)
    elif "-" in text and "202" in text:
        try:
            full_match = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2})", text)
            if full_match: target_dt = datetime.datetime.strptime(full_match.group(1), "%Y-%m-%d %H:%M")
            else:
                d_match = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", text)
                if d_match: target_dt = datetime.datetime.strptime(d_match.group(1), "%Y-%m-%d"); target_dt = target_dt.replace(hour=23, minute=59)
        except: pass

    if target_dt:
        return (
            target_dt.strftime("%Y-%m-%d"), 
            f"{target_dt.month}月{target_dt.day}日 {target_dt.hour:02d}:{target_dt.minute:02d}",
            int(target_dt.timestamp() * 1000)
        )
    return None, text, 0

def auto_login(driver):
    print(">>> 正在自动登录...")
    driver.get("http://passport2.chaoxing.com/login?fid=&newversion=true&refer=http%3A%2F%2Fi.chaoxing.com")
    try:
        try: driver.find_element(By.XPATH, "//div[contains(text(), '手机') or contains(text(), '账号')]").click(); time.sleep(0.5)
        except: pass
        try: u = driver.find_element(By.ID, "phone")
        except: u = driver.find_element(By.ID, "uname")
        u.clear(); u.send_keys(USERNAME)
        p = driver.find_element(By.ID, "pwd"); p.clear(); p.send_keys(PASSWORD)
        try: driver.execute_script("document.getElementById('agree').checked = true;")
        except: pass
        driver.find_element(By.ID, "loginBtn").click()
        for i in range(15):
            time.sleep(1)
            if "i.chaoxing.com" in driver.current_url: print(">>> 自动登录成功！"); return True
        WebDriverWait(driver, 60).until(EC.url_contains("i.chaoxing.com"))
    except Exception as e: input(">>> 手动登录后回车...")

def main():
    # 注册自定义协议
    register_protocol()

    # 获取路径（确保 main() 内外都能正确获取）
    if getattr(sys, 'frozen', False):
        main_base_path = os.path.dirname(sys.executable)
    else:
        main_base_path = os.path.dirname(os.path.abspath(__file__))

    # === 【这里是本次优化的核心代码】 ===
    edge_options = webdriver.EdgeOptions()
    # 策略设置为 eager：DOM加载完就认为好了，不等图片和烂七八糟的脚本
    edge_options.page_load_strategy = 'eager' 
    
    driver = webdriver.Edge(service=SERVICE, options=edge_options)
    
    # 设置页面加载超时时间为 15秒
    # 如果15秒还在转圈，直接抛出异常，我们在下面捕获它并继续执行，不再死等
    driver.set_page_load_timeout(15) 
    driver.implicitly_wait(2)
    # =================================

    auto_login(driver)

    print(f">>> [阶段1] 获取前 {MAX_COURSES_COUNT} 门课程...")
    all_courses = []
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "frame_content")))
        driver.switch_to.frame("frame_content")
        elements = driver.find_elements(By.CLASS_NAME, "course-name")
        for span in elements:
            try:
                title = span.text.strip()
                parent_a = span.find_element(By.XPATH, "./..")
                href = parent_a.get_attribute("href")
                if title and href: all_courses.append({"title": title, "url": href})
            except: continue
    except: pass
    driver.switch_to.default_content()

    target_courses = all_courses[:MAX_COURSES_COUNT]
    print(f">>> 锁定 {len(target_courses)} 门课，启动【增量同步爬取】...")
    print("-" * 40)
    
    new_fetched_tasks = []

    for index, course in enumerate(target_courses):
        print(f"[{index+1}/{len(target_courses)}] {course['title']} ...", end="")
        try:
            raw_url = course['url']
            target_url = re.sub(r"pageHeader=\d+", "pageHeader=8", raw_url) if "pageHeader=" in raw_url else raw_url + "&pageHeader=8"
            
            # 【这里加了防卡死处理】
            try:
                driver.get(target_url)
            except Exception:
                # 如果超时报错，只要页面里有东西，我们就可以继续
                # print(" (页面加载超时，尝试强制停止并继续...)")
                driver.execute_script("window.stop();")
            
            time.sleep(1) # 稍微喘口气
            
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if iframes: driver.switch_to.frame(iframes[-1])
            
            try: page_text = driver.find_element(By.TAG_NAME, "body").text
            except: print(" -> (空白)"); driver.switch_to.default_content(); continue
            
            lines = page_text.split('\n'); count = 0
            for i, line in enumerate(lines):
                if ("剩余" in line or "截止" in line):
                    context = line
                    if i>0: context += lines[i-1]
                    if i>1: context += lines[i-2]
                    if any(k in context for k in ["已完成", "已交", "已提交", "待批阅", "已互评"]): continue
                    
                    hw_title = "未命名作业"
                    if i>0:
                        prev = lines[i-1].strip()
                        status_kw = ["未交", "智能分析", "待批阅", "作业", "测验"]
                        if any(k in prev and len(prev)<10 for k in status_kw) and i>1: hw_title = lines[i-2].strip()
                        else: hw_title = prev if len(prev)>2 else line.split("截止")[0]
                    
                    sort_date, display_text, timestamp = get_deadline_details(line)
                    if sort_date:
                        unique_id = generate_task_id(course['title'], hw_title, sort_date)
                        new_fetched_tasks.append({
                            "id": unique_id,
                            "title": hw_title, 
                            "start": sort_date, 
                            "url": target_url,
                            "extendedProps": { 
                                "course": course['title'], 
                                "deadline_text": display_text, 
                                "source": "auto",
                                "status": "todo",
                                "timestamp": timestamp
                            }
                        })
                        count += 1
            print(f" -> 新抓取 {count} 个") if count>0 else print(" -> 无新待办")
            driver.switch_to.default_content()
        except Exception as e: print(f" -> 错: {repr(e)}"); driver.switch_to.default_content()

    # --- 网页生成部分 ---
    print("-" * 40)
    print(f">>> 抓取完成，正在生成任务管理系统...")
    
    now = datetime.datetime.now()
    today_title = f"{now.year}年{now.month}月{now.day}日"
    fetched_json = json.dumps(new_fetched_tasks, ensure_ascii=False)
    
    html_filename = "my_calendar_final.html"
    html_path = os.path.join(main_base_path, html_filename)

    html = '''
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset='utf-8' />
    <title>学习通任务管理 ''' + today_title + '''</title>
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js'></script>
    <style>
        :root {
            --primary-blue: #667EEA;
            --primary-blue-light: #7C8EF0;
            --primary-blue-dark: #5A6FD6;
            --secondary-orange: #FF9F43;
            --secondary-orange-light: #FFB366;
            --secondary-orange-dark: #E68E39;
            --success-green: #26DE81;
            --success-green-light: #45E892;
            --success-green-dark: #1FC46D;
            --bg-light: #F5F7FC;
            --bg-card: #FFFFFF;
            --status-done-bg: #E8F9F0;
            --status-done-border: #26DE81;
            --status-manual-bg: #FFF4E6;
            --status-manual-border: #FF9F43;
            --status-auto-bg: #EBF3FF;
            --status-auto-border: #667EEA;
            --text-primary: #2D3748;
            --text-secondary: #718096;
            --text-muted: #A0AEC0;
            --shadow-sm: 0 2px 8px rgba(0,0,0,0.08);
            --shadow-md: 0 4px 20px rgba(0,0,0,0.12);
            --shadow-lg: 0 8px 30px rgba(0,0,0,0.16);
            --shadow-neumorphic: 6px 6px 12px rgba(0,0,0,0.08), -6px -6px 12px rgba(255,255,255,0.9);
            --glass-bg: rgba(255, 255, 255, 0.85);
            --glass-backdrop: rgba(102, 126, 234, 0.15);
            --glass-border: rgba(255, 255, 255, 0.5);
            --transition-fast: 0.15s ease;
            --transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --transition-bounce: 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, var(--bg-light) 0%, #E8ECFB 100%);
            min-height: 100vh;
            color: var(--text-primary);
        }

        .header-section {
            background: linear-gradient(135deg, var(--primary-blue) 0%, #764BA2 100%);
            padding: 30px 40px;
            border-radius: var(--radius-lg);
            margin-bottom: 24px;
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
        }

        .header-section::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 300px;
            height: 300px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        }

        .header-section::after {
            content: '';
            position: absolute;
            bottom: -30%;
            left: 10%;
            width: 200px;
            height: 200px;
            background: rgba(255,255,255,0.08);
            border-radius: 50%;
        }

        .header-section h2 {
            text-align: center;
            color: #ffffff;
            margin-bottom: 0;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 1px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
            z-index: 1;
        }

        .header-subtitle {
            text-align: center;
            color: rgba(255,255,255,0.8);
            font-size: 14px;
            margin-top: 8px;
            position: relative;
            z-index: 1;
        }

        #calendar {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--bg-card);
            padding: 24px;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-neumorphic);
        }

        .fc { font-family: inherit; }
        .fc-toolbar-title {
            font-size: 22px !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
        }
        .fc-button {
            border-radius: var(--radius-sm) !important;
            font-weight: 600 !important;
            transition: var(--transition-normal) !important;
        }
        .fc-button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-sm) !important;
        }
        .fc-daygrid-day-number {
            font-weight: 500;
            color: var(--text-secondary);
        }
        .fc-day-today {
            background: var(--glass-backdrop) !important;
        }

        .fc-event { border: none !important; background: transparent !important; margin-bottom: 6px !important; cursor: pointer; }
        .task-link { text-decoration: none; display: block; }

        .my-task-card {
            background: var(--bg-card);
            border-radius: var(--radius-md);
            padding: 12px 14px;
            margin-bottom: 8px;
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-normal);
            position: relative;
            border-left: 4px solid transparent;
            overflow: hidden;
        }

        .my-task-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
        }

        .my-task-card:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
        }

        .my-task-card.done {
            background: linear-gradient(135deg, var(--status-done-bg) 0%, rgba(38, 222, 129, 0.1) 100%);
            border-left-color: var(--status-done-border);
            opacity: 0.8;
        }
        .my-task-card.done .course-tag {
            color: var(--success-green-dark);
            text-decoration: line-through;
        }
        .my-task-card.done .hw-name {
            text-decoration: line-through;
            color: var(--text-muted);
        }

        .my-task-card.manual.todo {
            background: linear-gradient(135deg, var(--status-manual-bg) 0%, rgba(255, 159, 67, 0.1) 100%);
            border-left-color: var(--status-manual-border);
        }
        .my-task-card.manual.todo .course-tag { color: var(--secondary-orange-dark); }

        .my-task-card.auto.todo {
            background: linear-gradient(135deg, var(--status-auto-bg) 0%, rgba(102, 126, 234, 0.1) 100%);
            border-left-color: var(--status-auto-border);
        }
        .my-task-card.auto.todo .course-tag { color: var(--primary-blue-dark); }

        .course-tag {
            font-weight: 700;
            font-size: 12px;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .course-tag::before {
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: currentColor;
        }

        .hw-name { font-weight: 600; font-size: 14px; color: var(--text-primary); margin-bottom: 8px; line-height: 1.5; white-space: normal; }
        .ddl-tag {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(255,255,255,0.9);
            border: 1px solid rgba(0,0,0,0.08);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .btn-group { position: fixed; bottom: 40px; right: 40px; display: flex; flex-direction: column; gap: 16px; z-index: 999; }

        .float-btn {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            color: white;
            text-align: center;
            line-height: 56px;
            font-size: 24px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
            cursor: pointer;
            transition: all var(--transition-bounce);
            text-decoration: none;
            border: none;
            outline: none;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .float-btn:hover {
            transform: scale(1.1) translateY(-4px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.3);
        }

        .btn-add {
            background: linear-gradient(135deg, var(--secondary-orange) 0%, var(--secondary-orange-dark) 100%);
            width: 64px;
            height: 64px;
            font-size: 32px;
        }
        .btn-add::after {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            border: 2px solid var(--secondary-orange);
            opacity: 0;
            animation: pulseRing 2s ease-out infinite;
        }
        @keyframes pulseRing {
            0% { transform: scale(1); opacity: 0.6; }
            100% { transform: scale(1.3); opacity: 0; }
        }

        .btn-clean { background: linear-gradient(135deg, var(--success-green) 0%, var(--success-green-dark) 100%); }
        .btn-backup { background: linear-gradient(135deg, #764BA2 0%, var(--primary-blue) 100%); }
        .btn-restore { background: linear-gradient(135deg, var(--text-secondary) 0%, var(--text-primary) 100%); }
        .btn-refresh { background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%); }

        .float-btn[data-tooltip]:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            right: 74px;
            top: 50%;
            transform: translateY(-50%);
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
            color: #fff;
            padding: 8px 16px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;
            box-shadow: var(--shadow-md);
            animation: tooltipIn 0.2s ease forwards;
        }
        @keyframes tooltipIn {
            from { opacity: 0; transform: translateY(-50%) translateX(10px); }
            to { opacity: 1; transform: translateY(-50%) translateX(0); }
        }

        .action-btns { position: absolute; top: 8px; right: 8px; display: none; gap: 6px; z-index: 2; }
        .my-task-card:hover .action-btns { display: flex; }
        .tiny-btn {
            cursor: pointer;
            font-weight: bold;
            width: 26px;
            height: 26px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            color: var(--text-muted);
            background: rgba(255,255,255,0.9);
            border-radius: 50%;
            transition: var(--transition-fast);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .tiny-btn:hover {
            background: var(--primary-blue);
            color: white;
            transform: scale(1.1);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        }
        .btn-check { color: var(--success-green); }
        .btn-undo { color: var(--secondary-orange); }

        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(45, 55, 72, 0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            animation: fadeIn 0.2s ease;
        }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

        .modal-content {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 32px;
            border-radius: var(--radius-lg);
            width: 380px;
            max-width: 90vw;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--glass-border);
            animation: slideUp 0.3s ease;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .modal-content h3 {
            margin-top: 0; margin-bottom: 24px;
            font-size: 20px; font-weight: 700;
            color: var(--text-primary);
            display: flex; align-items: center; gap: 10px;
        }

        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block; margin-bottom: 8px;
            font-weight: 600; font-size: 13px;
            color: var(--text-secondary);
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .form-group input {
            width: 100%; padding: 14px 16px;
            border: 2px solid transparent;
            background: rgba(245, 247, 250, 0.8);
            border-radius: var(--radius-sm);
            font-size: 15px; color: var(--text-primary);
            box-sizing: border-box;
            transition: var(--transition-fast);
            box-shadow: inset 2px 2px 4px rgba(0,0,0,0.04), inset -2px -2px 4px rgba(255,255,255,0.8);
        }
        .form-group input:focus {
            outline: none; border-color: var(--primary-blue);
            background: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }

        .modal-btns { display: flex; justify-content: flex-end; gap: 12px; margin-top: 28px; }
        .modal-btn {
            padding: 12px 24px;
            border-radius: var(--radius-sm);
            font-size: 14px; font-weight: 600;
            cursor: pointer; transition: var(--transition-normal);
            border: none; outline: none;
        }
        .modal-btn-cancel { background: rgba(160, 174, 192, 0.2); color: var(--text-secondary); }
        .modal-btn-cancel:hover { background: rgba(160, 174, 192, 0.4); transform: translateY(-2px); }
        .modal-btn-save {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .modal-btn-save:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4); }
    </style>
    </head>
    <body>
  <div class="header-section">
    <h2>📅 学习通任务管理</h2>
    <div class="header-subtitle">''' + today_title + ''' · 按时完成每一天的学习任务</div>
  </div>
  <div id='calendar'></div>

  <div class="btn-group">
    <button class="float-btn btn-add" onclick="openModal()" data-tooltip="添加手动任务">+</button>
    <button class="float-btn btn-clean" onclick="autoCompleteExpired()" data-tooltip="归档过期任务">✓</button>
    <button class="float-btn btn-backup" onclick="backupData()" data-tooltip="备份数据">📥</button>
    <button class="float-btn btn-restore" onclick="triggerRestore()" data-tooltip="恢复数据">📤</button>
    <a href="cxcalendar://run" class="float-btn btn-refresh" data-tooltip="同步学习通">↻</a>
  </div>

  <input type="file" id="restoreInput" style="display:none" onchange="handleFile(this)">

  <div id="addModal" class="modal">
    <div class="modal-content">
        <h3>📝 任务详情</h3>
        <div class="form-group">
            <label>课程名称</label>
            <input type="text" id="mCourse" placeholder="请输入课程名称">
        </div>
        <div class="form-group">
            <label>作业内容</label>
            <input type="text" id="mTitle" placeholder="请输入作业描述">
        </div>
        <div class="form-group">
            <label>截止时间</label>
            <input type="datetime-local" id="mDate">
        </div>
        <div class="form-group">
            <label>链接 (可选)</label>
            <input type="text" id="mLink" placeholder="https://...">
        </div>
        <div class="modal-btns">
            <button class="modal-btn modal-btn-cancel" onclick="closeModal()">取消</button>
            <button class="modal-btn modal-btn-save" onclick="saveManualTask()">保存</button>
        </div>
    </div>
  </div>

    <script>
      var fetchedTasks = ''' + fetched_json + ''';
      var editingId = null;

      document.addEventListener('DOMContentLoaded', function() {
        syncData();
        renderCalendar();
        animateTaskCards();
      });

      function animateTaskCards() {
        const cards = document.querySelectorAll('.my-task-card');
        cards.forEach((card, index) => {
          card.style.opacity = '0';
          card.style.transform = 'translateY(20px)';
          setTimeout(() => {
            card.style.transition = 'all 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, index * 50);
        });
      }

      function syncData() {
        var localDB = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        fetchedTasks.forEach(newItem => {
            let exists = localDB.find(item => item.id === newItem.id);
            if (!exists) localDB.push(newItem);
        });
        localStorage.setItem('chaoxing_db', JSON.stringify(localDB));
      }

      function backupData() {
        var data = localStorage.getItem('chaoxing_db');
        if (!data || data === '[]') { alert('当前没有数据可备份！'); return; }
        var blob = new Blob([data], {type: "application/json"});
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        var dateStr = new Date().toISOString().split('T')[0].replace(/-/g, '');
        a.download = "学习通备份_" + dateStr + ".json";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }

      function triggerRestore() { document.getElementById('restoreInput').click(); }

      function handleFile(input) {
        var file = input.files[0];
        if (!file) return;
        if (!confirm('恢复数据将【覆盖】当前所有任务进度，确定要继续吗？')) { input.value = ''; return; }
        var reader = new FileReader();
        reader.onload = function(e) {
            try {
                var data = JSON.parse(e.target.result);
                if (Array.isArray(data)) {
                    localStorage.setItem('chaoxing_db', JSON.stringify(data));
                    alert('数据恢复成功！页面即将刷新。');
                    location.reload();
                } else { alert('文件格式错误'); }
            } catch(err) { alert('读取失败'); }
        };
        reader.readAsText(file);
      }

      function autoCompleteExpired() {
        if(!confirm('归档过期任务？')) return;
        var localDB = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        var nowTimestamp = Date.now();
        localDB.forEach(task => {
            if (task.extendedProps.status !== 'done' && task.extendedProps.timestamp && task.extendedProps.timestamp < nowTimestamp) {
                task.extendedProps.status = 'done';
            }
        });
        localStorage.setItem('chaoxing_db', JSON.stringify(localDB));
        renderCalendar();
      }

      function renderCalendar() {
        var tasks = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        // 如果localStorage为空，使用fetchedTasks
        if (tasks.length === 0) {
          tasks = fetchedTasks;
          // 同时更新localStorage
          localStorage.setItem('chaoxing_db', JSON.stringify(tasks));
        }
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
          locale: 'zh-cn',
          contentHeight: 'auto',
          dayMaxEvents: false,
          events: tasks,
          eventContent: function(arg) {
            let props = arg.event.extendedProps;
            let status = props.status;
            let source = props.source || '';
            let id = arg.event.id;

            // Status icon
            let statusIcon = status === 'done'
                ? '<span style="color:var(--success-green)">●</span>'
                : '<span style="color:var(--text-muted)">○</span>';

            // Source icon
            let sourceIcon = source === 'manual'
                ? '<span style="margin-left:4px">✏️</span>'
                : '<span style="margin-left:4px">🔗</span>';

            let cardClass = 'my-task-card ' + source + ' ' + status;
            let actionHtml = '';

            if (status === 'done')
                actionHtml += `<span class="tiny-btn btn-undo" onclick="toggleStatus('${id}', 'todo', event)">↩</span>`;
            else
                actionHtml += `<span class="tiny-btn btn-check" onclick="toggleStatus('${id}', 'done', event)">✓</span>`;

            if (source === 'manual')
                actionHtml += `<span class="tiny-btn" onclick="editTask('${id}', event)">✎</span>`;
            actionHtml += `<span class="tiny-btn" onclick="deleteTask('${id}', event)">×</span>`;

            let content = '<div class="' + cardClass + '">' +
                        '<div class="action-btns">' + actionHtml + '</div>' +
                        '<div class="course-tag">' + statusIcon + ' ' + props.course + sourceIcon + '</div>' +
                        '<div class="hw-name">' + arg.event.title + '</div>' +
                        '<div class="ddl-tag">⏰ ' + props.deadline_text + '</div>' +
                        '</div>';

            if(arg.event.url)
                return { 'html': '<a href="' + arg.event.url + '" target="_blank" class="task-link">' + content + '</a>' };
            else
                return { 'html': content };
          }
        });
        calendar.render();
      }

      function toggleStatus(id, newStatus, e) {
        e.preventDefault(); e.stopPropagation();
        updateTask(id, t => t.extendedProps.status = newStatus);
      }

      function deleteTask(id, e) {
        e.preventDefault(); e.stopPropagation();
        if(confirm('确定删除吗？')) {
            var db = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
            db = db.filter(t => t.id !== id);
            localStorage.setItem('chaoxing_db', JSON.stringify(db));
            renderCalendar();
        }
      }

      function editTask(id, e) {
        e.preventDefault(); e.stopPropagation();
        var db = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        var task = db.find(t => t.id === id);
        if(task) {
            editingId = id;
            document.getElementById('mCourse').value = task.extendedProps.course;
            document.getElementById('mTitle').value = task.title;
            if(task.start && task.start.includes('T')) document.getElementById('mDate').value = task.start;
            else document.getElementById('mDate').value = task.start + 'T23:59';
            document.getElementById('mLink').value = task.url || '';
            document.getElementById('addModal').style.display = 'flex';
        }
      }

      function updateTask(id, callback) {
        var db = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        var task = db.find(t => t.id === id);
        if(task) {
            callback(task);
            localStorage.setItem('chaoxing_db', JSON.stringify(db));
            renderCalendar();
        }
      }

      function openModal() { editingId=null; document.querySelectorAll('input').forEach(i=>i.value=''); document.getElementById('addModal').style.display='flex'; }
      function closeModal() { document.getElementById('addModal').style.display='none'; }
      
      function saveManualTask() {
        let course = document.getElementById('mCourse').value.trim() || '自定义';
        let title = document.getElementById('mTitle').value.trim() || '未命名';
        let dInput = document.getElementById('mDate').value;
        let link = document.getElementById('mLink').value.trim();
        
        let dateObj = dInput ? new Date(dInput) : new Date();
        let dateStr = dInput ? dInput.split('T')[0] : dateObj.toISOString().split('T')[0];
        let displayStr = (dateObj.getMonth()+1) + '月' + dateObj.getDate() + '日';
        if(dInput && dInput.includes('T')) displayStr += ' ' + dateObj.getHours() + ':' + dateObj.getMinutes();

        let newTask = {
            id: editingId || 'manual_' + Date.now(),
            title: title,
            start: dateStr,
            url: link,
            extendedProps: {
                course: course,
                deadline_text: displayStr,
                source: 'manual',
                status: 'todo',
                timestamp: dateObj.getTime()
            }
        };

        var db = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        if(editingId) {
            let idx = db.findIndex(t => t.id === editingId);
            if(idx!==-1) db[idx] = newTask;
        } else {
            db.push(newTask);
        }
        localStorage.setItem('chaoxing_db', JSON.stringify(db));
        closeModal();
        renderCalendar();
      }
    </script>
    </body>
    </html>
    '''

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f">>> 网页已生成：{html_path}")
    
    webbrowser.open('file://' + html_path)
    driver.quit()
    print(">>> 程序已完成，3秒后自动退出...")
    time.sleep(3)
    sys.exit()

import traceback

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
