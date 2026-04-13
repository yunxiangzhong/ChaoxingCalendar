import sys
import os
import time
import re
import json
import datetime
import hashlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
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

USERNAME = "19914770930" 
PASSWORD = "Zyx1727236047@"

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
            exe_path = os.path.join(base_path, "dist", "crawl.exe")
        
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

def crawl_tasks():
    # 注册自定义协议
    register_protocol()

    # 获取路径
    if getattr(sys, 'frozen', False):
        main_base_path = os.path.dirname(sys.executable)
    else:
        main_base_path = os.path.dirname(os.path.abspath(__file__))

    # 配置 Edge 浏览器
    edge_options = webdriver.EdgeOptions()
    edge_options.page_load_strategy = 'eager' 
    # 添加更多配置选项
    # 移除无头模式，以便用户可以手动登录
    # edge_options.add_argument('--headless')  # 无头模式
    edge_options.add_argument('--disable-gpu')  # 禁用GPU
    edge_options.add_argument('--no-sandbox')  # 禁用沙箱
    edge_options.add_argument('--disable-dev-shm-usage')  # 禁用开发者共享内存
    edge_options.add_argument('--disable-extensions')  # 禁用扩展
    
    print(f">>> 正在初始化 Edge WebDriver...")
    print(f">>> 驱动路径: {driver_path if os.path.exists(driver_path) else '系统默认'}")
    
    # 强制绕过本地代理，避免 Bad Gateway 错误
    os.environ['no_proxy'] = 'localhost,127.0.0.1'
    
    try:
        driver = webdriver.Edge(service=SERVICE, options=edge_options)
        print(">>> Edge WebDriver 初始化成功！")
    except Exception as e:
        print(f">>> Edge WebDriver 初始化失败: {e}")
        # 尝试使用系统默认驱动
        print(">>> 尝试使用系统默认驱动...")
        try:
            # 确保系统默认驱动也绕过本地代理
            os.environ['no_proxy'] = 'localhost,127.0.0.1'
            driver = webdriver.Edge(options=edge_options)
            print(">>> 系统默认驱动初始化成功！")
        except Exception as e2:
            print(f">>> 系统默认驱动初始化也失败: {e2}")
            raise
    
    # 设置页面加载超时时间为 15秒
    driver.set_page_load_timeout(15) 
    driver.implicitly_wait(2)

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
            
            # 防卡死处理
            try:
                driver.get(target_url)
            except Exception:
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

    driver.quit()
    return new_fetched_tasks
