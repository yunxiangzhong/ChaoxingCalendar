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

# ================= 路径锁定 =================
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
driver_path = os.path.join(base_path, "msedgedriver.exe")
# ===========================================

SERVICE = Service(driver_path) 
#输入最大课程的数量（一般只需要爬本学期的课程
MAX_COURSES_COUNT = 10 

# 输入你的账号和密码
USERNAME = "xxx" 
PASSWORD = "xxx"
# ===========================================

# --- 辅助函数 ---
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
    html_path = os.path.join(base_path, html_filename)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset='utf-8' />
    <title>学习通任务管理 ({today_title})</title>
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js'></script>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; padding: 20px; background-color: #f0f2f5; }}
        h2 {{ text-align: center; color: #333; margin-bottom: 20px; }}
        #calendar {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        
        .fc-event {{ border: none !important; background: transparent !important; margin-bottom: 6px !important; cursor: pointer; }}
        .task-link {{ text-decoration: none; display: block; }}
        
        /* 状态样式 */
        .my-task-card.done {{ background-color: #f6ffed; border-left: 4px solid #52c41a; border: 1px solid #b7eb8f; opacity: 0.7; }}
        .my-task-card.done .course-tag {{ color: #52c41a; text-decoration: line-through; }}
        .my-task-card.done .hw-name {{ text-decoration: line-through; color: #999; }}
        
        .my-task-card.manual.todo {{ background-color: #fff7e6; border-left: 4px solid #fa8c16; border: 1px solid #ffd591; }}
        .my-task-card.manual.todo .course-tag {{ color: #fa8c16; }}

        .my-task-card.auto.todo {{ background-color: #e6f7ff; border-left: 4px solid #1890ff; border: 1px solid #91d5ff; }}
        .my-task-card.auto.todo .course-tag {{ color: #1890ff; }}

        .my-task-card {{ padding: 6px 10px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; position: relative; }}
        .my-task-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 10; }}
        
        .course-tag {{ font-weight: bold; font-size: 12px; margin-bottom: 2px; }}
        .hw-name {{ font-weight: 600; font-size: 13px; color: #333; margin-bottom: 4px; line-height: 1.4; white-space: normal; }}
        .ddl-tag {{ display: inline-block; background: #fff; border: 1px solid #ddd; padding: 1px 5px; border-radius: 3px; font-size: 11px; color: #666; font-weight: 500; }}
        
        /* 按钮组 */
        .btn-group {{ position: fixed; bottom: 40px; right: 40px; display: flex; flex-direction: column; gap: 15px; z-index: 999; }}
        .float-btn {{ width: 50px; height: 50px; border-radius: 50%; color: white; text-align: center; line-height: 50px; font-size: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); cursor: pointer; transition: all 0.3s; text-decoration: none; border: none; outline: none; }}
        .btn-refresh {{ background-color: #1890ff; }}
        .btn-add {{ background-color: #fa8c16; font-size: 28px; }}
        .btn-clean {{ background-color: #52c41a; }}
        .btn-backup {{ background-color: #722ed1; }}
        .btn-restore {{ background-color: #595959; }}
        .float-btn:hover {{ transform: scale(1.1); filter: brightness(1.1); }}
        
        .float-btn[title]:hover::after {{ content: attr(title); position: absolute; right: 60px; top: 10px; background: rgba(0,0,0,0.8); color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap; }}

        .action-btns {{ position: absolute; top: 2px; right: 2px; display: none; gap: 4px; }}
        .my-task-card:hover .action-btns {{ display: flex; }}
        .tiny-btn {{ cursor: pointer; font-weight: bold; padding: 0 4px; font-size: 14px; color: #aaa; border-radius: 3px; }}
        .tiny-btn:hover {{ background: rgba(0,0,0,0.05); color: #333; }}
        .btn-check {{ color: #52c41a; }}
        .btn-undo {{ color: #fa8c16; }}
        
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center; }}
        .modal-content {{ background: white; padding: 25px; border-radius: 12px; width: 340px; }}
        .form-group {{ margin-bottom: 12px; }}
        .form-group label {{ display: block; margin-bottom: 4px; font-weight: bold; }}
        .form-group input {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .modal-btns {{ display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }}
    </style>
    </head>
    <body>
      <h2>📅 学习通任务管理 ({today_title})</h2>
      <div id='calendar'></div>

      <div class="btn-group">
        <button class="float-btn btn-add" onclick="openModal()" title="添加任务">+</button>
        <button class="float-btn btn-clean" onclick="autoCompleteExpired()" title="归档过期任务">✓</button>
        <button class="float-btn btn-backup" onclick="backupData()" title="备份数据">📥</button>
        <button class="float-btn btn-restore" onclick="triggerRestore()" title="恢复数据">📤</button>
        <a href="cxcalendar://run" class="float-btn btn-refresh" title="同步学习通">↻</a>
      </div>

      <input type="file" id="restoreInput" style="display:none" onchange="handleFile(this)">

      <div id="addModal" class="modal">
        <div class="modal-content">
            <h3 style="margin-top:0" id="modalTitle">任务详情</h3>
            <div class="form-group"><label>课程名称</label><input type="text" id="mCourse"></div>
            <div class="form-group"><label>作业内容</label><input type="text" id="mTitle"></div>
            <div class="form-group"><label>截止时间</label><input type="datetime-local" id="mDate"></div>
            <div class="form-group"><label>链接 (可选)</label><input type="text" id="mLink"></div>
            <div class="modal-btns">
                <button onclick="closeModal()" style="padding:8px 16px;">取消</button>
                <button onclick="saveManualTask()" style="padding:8px 16px; background:#1890ff; color:white; border:none;">保存</button>
            </div>
        </div>
      </div>

    <script>
      var fetchedTasks = {fetched_json}; 
      var editingId = null;

      document.addEventListener('DOMContentLoaded', function() {{
        syncData();
        renderCalendar();
      }});

      function syncData() {{
        var localDB = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        fetchedTasks.forEach(newItem => {{
            let exists = localDB.find(item => item.id === newItem.id);
            if (!exists) localDB.push(newItem);
        }});
        localStorage.setItem('chaoxing_db', JSON.stringify(localDB));
      }}

      function backupData() {{
        var data = localStorage.getItem('chaoxing_db');
        if (!data || data === '[]') {{ alert('当前没有数据可备份！'); return; }}
        var blob = new Blob([data], {{type: "application/json"}});
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        var dateStr = new Date().toISOString().split('T')[0].replace(/-/g, '');
        a.download = "学习通备份_" + dateStr + ".json";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }}

      function triggerRestore() {{ document.getElementById('restoreInput').click(); }}

      function handleFile(input) {{
        var file = input.files[0];
        if (!file) return;
        if (!confirm('恢复数据将【覆盖】当前所有任务进度，确定要继续吗？')) {{ input.value = ''; return; }}
        var reader = new FileReader();
        reader.onload = function(e) {{
            try {{
                var data = JSON.parse(e.target.result);
                if (Array.isArray(data)) {{
                    localStorage.setItem('chaoxing_db', JSON.stringify(data));
                    alert('数据恢复成功！页面即将刷新。');
                    location.reload();
                }} else {{ alert('文件格式错误'); }}
            }} catch(err) {{ alert('读取失败'); }}
        }};
        reader.readAsText(file);
      }}

      function autoCompleteExpired() {{
        if(!confirm('归档过期任务？')) return;
        var localDB = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        var nowTimestamp = Date.now();
        localDB.forEach(task => {{
            if (task.extendedProps.status !== 'done' && task.extendedProps.timestamp && task.extendedProps.timestamp < nowTimestamp) {{
                task.extendedProps.status = 'done';
            }}
        }});
        localStorage.setItem('chaoxing_db', JSON.stringify(localDB));
        renderCalendar();
      }}

      function renderCalendar() {{
        var tasks = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        var calendarEl = document.getElementById('calendar');
        var calendar = new FullCalendar.Calendar(calendarEl, {{
          initialView: 'dayGridMonth',
          locale: 'zh-cn',
          contentHeight: 'auto',
          dayMaxEvents: false,
          events: tasks,
          eventContent: function(arg) {{
            let props = arg.event.extendedProps;
            let status = props.status; 
            let source = props.source; 
            let id = arg.event.id;
            
            let cardClass = `my-task-card ${{source}} ${{status}}`;
            let actionHtml = '';
            
            if (status === 'done') actionHtml += `<span class="tiny-btn btn-undo" onclick="toggleStatus('${{id}}', 'todo', event)">↩</span>`;
            else actionHtml += `<span class="tiny-btn btn-check" onclick="toggleStatus('${{id}}', 'done', event)">✓</span>`;
            
            if (source === 'manual') actionHtml += `<span class="tiny-btn" onclick="editTask('${{id}}', event)">✎</span>`;
            actionHtml += `<span class="tiny-btn" onclick="deleteTask('${{id}}', event)">×</span>`;
            
            let content = `
                <div class="${{cardClass}}">
                    <div class="action-btns">${{actionHtml}}</div>
                    <div class="course-tag">📌 ${{props.course}}</div>
                    <div class="hw-name">${{arg.event.title}}</div>
                    <div class="ddl-tag">⏰ ${{props.deadline_text}}</div>
                </div>
            `;
            if(arg.event.url) return {{ html: `<a href="${{arg.event.url}}" target="_blank" class="task-link">${{content}}</a>` }};
            else return {{ html: content }};
          }}
        }});
        calendar.render();
      }}

      function toggleStatus(id, newStatus, e) {{
        e.preventDefault(); e.stopPropagation();
        updateTask(id, t => t.extendedProps.status = newStatus);
      }}

      function deleteTask(id, e) {{
        e.preventDefault(); e.stopPropagation();
        if(confirm('确定删除吗？')) {{
            var db = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
            db = db.filter(t => t.id !== id);
            localStorage.setItem('chaoxing_db', JSON.stringify(db));
            renderCalendar();
        }}
      }}

      function editTask(id, e) {{
        e.preventDefault(); e.stopPropagation();
        var db = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        var task = db.find(t => t.id === id);
        if(task) {{
            editingId = id;
            document.getElementById('mCourse').value = task.extendedProps.course;
            document.getElementById('mTitle').value = task.title;
            if(task.start && task.start.includes('T')) document.getElementById('mDate').value = task.start;
            else document.getElementById('mDate').value = task.start + 'T23:59';
            document.getElementById('mLink').value = task.url || '';
            document.getElementById('addModal').style.display = 'flex';
        }}
      }}

      function updateTask(id, callback) {{
        var db = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        var task = db.find(t => t.id === id);
        if(task) {{
            callback(task);
            localStorage.setItem('chaoxing_db', JSON.stringify(db));
            renderCalendar();
        }}
      }}

      function openModal() {{ editingId=null; document.querySelectorAll('input').forEach(i=>i.value=''); document.getElementById('addModal').style.display='flex'; }}
      function closeModal() {{ document.getElementById('addModal').style.display='none'; }}
      
      function saveManualTask() {{
        let course = document.getElementById('mCourse').value.trim() || '自定义';
        let title = document.getElementById('mTitle').value.trim() || '未命名';
        let dInput = document.getElementById('mDate').value;
        let link = document.getElementById('mLink').value.trim();
        
        let dateObj = dInput ? new Date(dInput) : new Date();
        let dateStr = dInput ? dInput.split('T')[0] : dateObj.toISOString().split('T')[0];
        let displayStr = `${{dateObj.getMonth()+1}}月${{dateObj.getDate()}}日`;
        if(dInput && dInput.includes('T')) displayStr += ` ${{dateObj.getHours()}}:${{dateObj.getMinutes()}}`;

        let newTask = {{
            id: editingId || 'manual_' + Date.now(),
            title: title,
            start: dateStr,
            url: link,
            extendedProps: {{
                course: course,
                deadline_text: displayStr,
                source: 'manual',
                status: 'todo',
                timestamp: dateObj.getTime()
            }}
        }};

        var db = JSON.parse(localStorage.getItem('chaoxing_db')) || [];
        if(editingId) {{
            let idx = db.findIndex(t => t.id === editingId);
            if(idx!==-1) db[idx] = newTask;
        }} else {{
            db.push(newTask);
        }}
        localStorage.setItem('chaoxing_db', JSON.stringify(db));
        closeModal();
        renderCalendar();
      }}
    </script>
    </body>
    </html>
    """
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f">>> 网页已生成：{html_path}")
    
    webbrowser.open('file://' + html_path)
    driver.quit()
    print(">>> 程序已完成，3秒后自动退出...")
    time.sleep(3)
    sys.exit()

if __name__ == "__main__":
    main()