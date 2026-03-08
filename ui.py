import sys
import os
import json
import datetime
import webbrowser

def generate_html(tasks):
    # 获取路径
    if getattr(sys, 'frozen', False):
        main_base_path = os.path.dirname(sys.executable)
    else:
        main_base_path = os.path.dirname(os.path.abspath(__file__))

    now = datetime.datetime.now()
    today_title = f"{now.year}年{now.month}月{now.day}日"
    fetched_json = json.dumps(tasks, ensure_ascii=False)
    
    html_filename = "my_calendar_final.html"
    html_path = os.path.join(main_base_path, html_filename)

    # ==================== Apple Minimalism Style ====================
    html = f'''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>学习通 · {today_title}</title>
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js"></script>
    <style>
        :root {{
            --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
            --accent: #0071E3;
            --accent-hover: #0077ED;
            --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --glass-bg: rgba(255, 255, 255, 0.7);
            --glass-border: rgba(255, 255, 255, 0.6);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --success: #10b981;
            --warning: #f59e0b;
            --border: rgba(226, 232, 240, 0.8);
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
            --shadow-lg: 0 8px 32px rgba(0,0,0,0.08);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            background: var(--bg-gradient);
            background-attachment: fixed;
            color: var(--text-primary);
            min-height: 100vh;
            padding: 48px 24px;
            line-height: 1.6;
            position: relative;
            overflow-x: hidden;
        }}

        /* 多层光晕背景 */
        body::before, body::after {{
            content: '';
            position: fixed;
            border-radius: 50%;
            pointer-events: none;
            z-index: -1;
        }}

        /* 主光晕 - 紫色 */
        body::before {{
            top: -20%;
            left: -10%;
            width: 80vw;
            height: 80vw;
            max-width: 600px;
            max-height: 600px;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.18) 0%, rgba(118, 75, 162, 0.1) 40%, transparent 70%);
            animation: float 20s ease-in-out infinite;
        }}

        /* 副光晕 - 青色 */
        body::after {{
            bottom: -10%;
            right: -5%;
            width: 60vw;
            height: 60vw;
            max-width: 500px;
            max-height: 500px;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.08) 40%, transparent 70%);
            animation: float 15s ease-in-out infinite reverse;
        }}

        @keyframes float {{
            0%, 100% {{ transform: translate(0, 0) scale(1); }}
            33% {{ transform: translate(30px, -30px) scale(1.05); }}
            66% {{ transform: translate(-20px, 20px) scale(0.95); }}
        }}

        /* 噪点纹理 - 增加质感 */
        .noise-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0.03;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctanes='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}

        .header {{
            margin-bottom: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 36px;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
            display: inline-block;
        }}

        .header p {{
            color: var(--text-secondary);
            font-size: 15px;
        }}

        .calendar-wrapper {{
            background: var(--glass-bg);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-lg);
            padding: 32px;
            margin-bottom: 120px;
            transition: var(--transition);
        }}

        .calendar-wrapper:hover {{
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
            transform: translateY(-2px);
        }}

        .fc {{ font-family: inherit; }}
        .fc-toolbar-title {{
            font-size: 22px !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
        }}
        .fc-button {{
            border-radius: var(--radius-sm) !important;
            font-weight: 600 !important;
            transition: var(--transition-normal) !important;
        }}
        .fc-button:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-sm) !important;
        }}
        .fc-daygrid-day-number {{
            font-weight: 500;
            color: var(--text-secondary);
        }}
        .fc-day-today {{
            background: var(--glass-backdrop) !important;
        }}

        .fc-event {{ border: none !important; background: transparent !important; margin-bottom: 6px !important; cursor: pointer; }}
        .task-link {{ text-decoration: none; display: block; }}

        .my-task-card {{
            background: var(--bg-card);
            border-radius: var(--radius-md);
            padding: 12px 14px;
            margin-bottom: 8px;
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-normal);
            position: relative;
            border-left: 4px solid transparent;
            overflow: hidden;
        }}

        .my-task-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
        }}

        .my-task-card:hover {{
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
        }}

        .my-task-card.done {{
            background: linear-gradient(135deg, var(--status-done-bg) 0%, rgba(38, 222, 129, 0.1) 100%);
            border-left-color: var(--status-done-border);
            opacity: 0.8;
        }}
        .my-task-card.done .course-tag {{
            color: var(--success-green-dark);
            text-decoration: line-through;
        }}
        .my-task-card.done .hw-name {{
            text-decoration: line-through;
            color: var(--text-muted);
        }}

        .my-task-card.manual.todo {{
            background: linear-gradient(135deg, var(--status-manual-bg) 0%, rgba(255, 159, 67, 0.1) 100%);
            border-left-color: var(--status-manual-border);
        }}
        .my-task-card.manual.todo .course-tag {{ color: var(--secondary-orange-dark); }}

        .my-task-card.auto.todo {{
            background: linear-gradient(135deg, var(--status-auto-bg) 0%, rgba(102, 126, 234, 0.1) 100%);
            border-left-color: var(--status-auto-border);
        }}
        .my-task-card.auto.todo .course-tag {{ color: var(--primary-blue-dark); }}

        .task-event {{ text-decoration: none; display: block; }}
        .task-card {{
            background: var(--system-bg);
            border-radius: var(--radius-md);
            padding: 14px 16px;
            margin-bottom: 10px;
            border-left: 3px solid var(--accent);
            transition: var(--transition);
            position: relative;
        }}
        .task-card:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-sm); }}
        .task-card.done {{ opacity: 0.5; border-left-color: var(--success); }}
        .task-card.auto {{ border-left-color: var(--accent); }}
        .task-card.manual {{ border-left-color: var(--warning); }}
        .task-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
        .task-status {{ width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }}
        .task-card.done .task-status {{ background: var(--success); }}
        .task-course {{ font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }}
        .task-title {{ font-size: 15px; font-weight: 500; color: var(--text-primary); margin-bottom: 8px; line-height: 1.4; }}
        .task-card.done .task-title {{ text-decoration: line-through; color: var(--text-secondary); }}
        .task-meta {{ display: flex; gap: 12px; font-size: 13px; color: var(--text-secondary); }}

        .task-actions {{ position: absolute; top: 12px; right: 12px; display: none; gap: 6px; }}
        .task-card:hover .task-actions {{ display: flex; }}
        .action-btn {{ width: 28px; height: 28px; border: none; background: var(--card-bg); border-radius: 50%; cursor: pointer; font-size: 14px; color: var(--text-secondary); box-shadow: var(--shadow-sm); }}
        .action-btn:hover {{ transform: scale(1.1); }}

        .fab-group {{ position: fixed; bottom: 32px; right: 32px; display: flex; flex-direction: column; align-items: flex-end; gap: 12px; z-index: 100; }}
        .fab {{ width: 52px; height: 52px; border-radius: 50%; border: none; background: var(--text-primary); color: white; font-size: 22px; cursor: pointer; box-shadow: var(--shadow-lg); transition: var(--transition); display: flex; align-items: center; justify-content: center; text-decoration: none; }}
        .fab:hover {{ transform: scale(1.05); box-shadow: 0 12px 40px rgba(0,0,0,0.2); }}
        .fab.main {{ width: 60px; height: 60px; background: var(--accent); }}
        .fab-label {{ position: absolute; right: 66px; background: var(--text-primary); color: white; padding: 6px 12px; border-radius: var(--radius-sm); font-size: 13px; white-space: nowrap; opacity: 0; transform: translateX(10px); transition: var(--transition); pointer-events: none; }}
        .fab:hover .fab-label {{ opacity: 1; transform: translateX(0); }}

        .modal {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); z-index: 1000; justify-content: center; align-items: center; animation: modalFadeIn 0.3s ease; }}

        @keyframes modalFadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}

        .modal-content {{ background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(32px); -webkit-backdrop-filter: blur(32px); border: 1px solid rgba(255, 255, 255, 0.5); border-radius: var(--radius-xl); width: 440px; max-width: 90vw; padding: 32px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15); animation: modalSlideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1); position: relative; overflow: hidden; }}

        .modal-content::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--accent-gradient); }}
        .modal-content h2 {{ font-size: 20px; font-weight: 600; margin-bottom: 24px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 8px; }}
        .form-group input {{ width: 100%; padding: 14px 16px; background: rgba(255, 255, 255, 0.6); border: 1px solid var(--border); border-radius: var(--radius-md); font-size: 15px; transition: var(--transition); color: var(--text-primary); }}
        .form-group input::placeholder {{ color: #94a3b8; }}
        .form-group input:hover {{ background: rgba(255, 255, 255, 0.8); border-color: #cbd5e1; }}
        .form-group input:focus {{ outline: none; border-color: #667eea; box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15); background: rgba(255, 255, 255, 0.95); }}
        .modal-btns {{ display: flex; justify-content: flex-end; gap: 12px; margin-top: 32px; }}
        .modal-btn {{ padding: 12px 24px; border-radius: var(--radius-md); font-size: 14px; font-weight: 600; cursor: pointer; transition: var(--transition); border: none; }}
        .modal-btn-cancel {{ background: rgba(241, 245, 249, 0.8); color: var(--text-primary); }}
        .modal-btn-cancel:hover {{ background: rgba(226, 232, 240, 0.9); transform: translateY(-1px); }}
        .modal-btn-save {{ background: var(--accent-gradient); color: white; box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35); }}
        .modal-btn-save:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.45); }}
        .modal-btn-save:active {{ transform: translateY(0); }}

        @media (max-width: 768px) {{
            body {{ padding: 24px 16px 100px; }}
            .header h1 {{ font-size: 28px; }}
            .calendar-wrapper {{ padding: 20px; margin-bottom: 100px; }}
            .fab-group {{ bottom: 24px; right: 24px; gap: 12px; }}
            .modal {{ align-items: flex-end; }}
            .modal-content {{ width: 100%; max-width: 100%; border-radius: var(--radius-xl) var(--radius-xl) 0 0; padding: 24px; animation: slideUpMobile 0.4s cubic-bezier(0.16, 1, 0.3, 1); }}
            @keyframes slideUpMobile {{ from {{ transform: translateY(100%); }} to {{ transform: translateY(0); }} }}
        }}
    </style>
    </head>
    <body>
  <div class="noise-overlay"></div>
  <div class="container">
    <header class="header">
      <h1>学习通任务管理</h1>
      <p>''' + today_title + '''</p>
    </header>

    <div class="calendar-wrapper">
      <div id="calendar"></div>
    </div>
  </div>

  <div class="fab-group">
    <a href="cxcalendar://run" class="fab" data-label="同步学习通">⟳</a>
    <button class="fab" onclick="triggerRestore()" data-label="恢复备份">⭳</button>
    <button class="fab" onclick="backupData()" data-label="备份数据">⭱</button>
    <button class="fab" onclick="autoCompleteExpired()" data-label="归档过期">✓</button>
    <button class="fab main" onclick="openModal()" data-label="添加任务">+</button>
  </div>

  <input type="file" id="restoreInput" style="display:none" onchange="handleFile(this)">

  <div id="addModal" class="modal">
    <div class="modal-content">
        <h3>添加任务</h3>
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
            let status = props.status || 'todo';
            let source = props.source || 'auto';
            let id = arg.event.id;
            let url = arg.event.url;

            let cardClass = 'task-card ' + source + ' ' + status;
            let icon = status === 'done' ? '✓' : '○';
            let sourceIcon = source === 'manual' ? '✎' : '🔗';

            let actions = '';
            if (status === 'done')
                actions = `<span class="action-btn done-btn" onclick="toggleStatus('${id}', 'todo', event)" title="标记未完成">↩</span>`;
            else
                actions = `<span class="action-btn done-btn" onclick="toggleStatus('${id}', 'done', event)" title="标记完成">✓</span>`;
            if (source === 'manual')
                actions += `<span class="action-btn" onclick="editTask('${id}', event)" title="编辑">✎</span>`;
            actions += `<span class="action-btn delete-btn" onclick="deleteTask('${id}', event)" title="删除">×</span>`;

            let html = '<div class="' + cardClass + '">' +
                '<div class="task-actions">' + actions + '</div>' +
                '<div class="task-header">' +
                '<span class="task-status"></span>' +
                '<span class="task-course">' + icon + ' ' + props.course + ' ' + sourceIcon + '</span>' +
                '</div>' +
                '<div class="task-title">' + arg.event.title + '</div>' +
                '<div class="task-meta"><span>⏱ ' + props.deadline_text + '</span></div>' +
                '</div>';

            if (url)
                return { html: '<a href="' + url + '" target="_blank" class="task-event" onclick="event.stopPropagation()">' + html + '</a>' };
            return { html: html };
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
    return html_path
