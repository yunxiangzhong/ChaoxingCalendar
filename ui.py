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

    # ==================== Claude Style ====================
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
            --bg: #FAF9F7;
            --surface: #FFFFFF;
            --surface-hover: #F5F4F2;
            --text-primary: #2D2D2D;
            --text-secondary: #888888;
            --text-muted: #BBBBBB;
            --border: #E5E5E5;
            --border-light: #EFEFEF;
            --accent-auto: #7A6855;
            --accent-manual: #A08040;
            --accent-done: #7A9B82;
            --accent-action: #2D2D2D;
            --shadow-xs: 0 1px 2px rgba(0,0,0,0.04);
            --shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
            --shadow-md: 0 4px 20px rgba(0,0,0,0.07);
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
            --radius-xl: 20px;
            --transition: all 0.2s ease;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            background: var(--bg);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 48px 24px 120px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1080px;
            margin: 0 auto;
        }}

        .header {{
            margin-bottom: 36px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 30px;
            font-weight: 600;
            letter-spacing: -0.3px;
            color: var(--text-primary);
            margin-bottom: 6px;
        }}

        .header p {{
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 400;
        }}

        .calendar-wrapper {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            padding: 28px;
        }}

        /* FullCalendar overrides */
        .fc {{ font-family: inherit; }}

        .fc-toolbar-title {{
            font-size: 18px !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
        }}

        .fc-button-primary {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            color: var(--text-primary) !important;
            border-radius: var(--radius-sm) !important;
            font-weight: 500 !important;
            font-size: 13px !important;
            box-shadow: var(--shadow-xs) !important;
            transition: var(--transition) !important;
            padding: 5px 12px !important;
        }}

        .fc-button-primary:hover {{
            background: var(--surface-hover) !important;
            border-color: #D0D0D0 !important;
            box-shadow: var(--shadow-sm) !important;
        }}

        .fc-button-primary:not(:disabled):active,
        .fc-button-primary:not(:disabled).fc-button-active {{
            background: var(--text-primary) !important;
            color: #FFF !important;
            border-color: var(--text-primary) !important;
            box-shadow: none !important;
        }}

        .fc-col-header-cell-cushion {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-decoration: none !important;
        }}

        .fc-daygrid-day-number {{
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            text-decoration: none !important;
            padding: 6px 8px !important;
        }}

        .fc-day-today {{
            background: #F7F3EE !important;
        }}

        .fc-day-today .fc-daygrid-day-number {{
            color: var(--accent-auto);
            font-weight: 700;
        }}

        .fc-daygrid-day-frame {{
            min-height: 80px !important;
        }}

        .fc-scrollgrid {{
            border-color: var(--border) !important;
        }}

        .fc-scrollgrid td, .fc-scrollgrid th {{
            border-color: var(--border-light) !important;
        }}

        .fc-event {{ border: none !important; background: transparent !important; margin-bottom: 3px !important; cursor: pointer; }}

        /* Task cards inside calendar cells */
        .task-card {{
            background: var(--surface);
            border-radius: var(--radius-sm);
            padding: 5px 8px;
            border-left: 3px solid var(--accent-auto);
            box-shadow: var(--shadow-xs);
            overflow: hidden;
            position: relative;
            transition: var(--transition);
        }}
        .task-card:hover {{
            background: var(--surface-hover);
            box-shadow: var(--shadow-sm);
        }}
        .task-card.done {{
            opacity: 0.55;
            border-left-color: var(--accent-done);
        }}
        .task-card.auto {{ border-left-color: var(--accent-auto); }}
        .task-card.manual {{ border-left-color: var(--accent-manual); }}

        .task-header {{
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 2px;
            overflow: hidden;
        }}

        .task-course {{
            font-size: 10px;
            font-weight: 600;
            color: var(--text-secondary);
            letter-spacing: 0.3px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
            min-width: 0;
        }}

        .task-badge {{
            font-size: 9px;
            flex-shrink: 0;
        }}

        .task-title {{
            font-size: 12px;
            font-weight: 500;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.4;
        }}

        .task-card.done .task-title {{
            text-decoration: line-through;
            color: var(--text-muted);
        }}

        .task-meta {{
            font-size: 10px;
            color: var(--text-muted);
            margin-top: 2px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .task-actions {{
            position: absolute;
            top: 4px;
            right: 4px;
            display: none;
            gap: 3px;
            background: var(--surface);
            border-radius: var(--radius-sm);
            padding: 2px;
            box-shadow: var(--shadow-sm);
        }}
        .task-card:hover .task-actions {{ display: flex; }}

        .action-btn {{
            width: 22px;
            height: 22px;
            border: none;
            background: transparent;
            border-radius: 4px;
            cursor: pointer;
            font-size: 11px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: var(--transition);
        }}
        .action-btn:hover {{
            background: var(--border);
            color: var(--text-primary);
        }}

        /* Floating action buttons */
        .fab-group {{
            position: fixed;
            bottom: 32px;
            right: 32px;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 10px;
            z-index: 100;
        }}

        .fab {{
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--text-primary);
            font-size: 18px;
            cursor: pointer;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
        }}
        .fab:hover {{
            background: var(--surface-hover);
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }}
        .fab.main {{
            width: 52px;
            height: 52px;
            font-size: 24px;
            background: var(--text-primary);
            color: #FFFFFF;
            border-color: var(--text-primary);
        }}
        .fab.main:hover {{
            background: #444444;
        }}

        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}

        .modal-content {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-xl);
            width: 420px;
            max-width: 92vw;
            padding: 28px;
            box-shadow: var(--shadow-md);
            position: relative;
        }}

        .modal-content h3 {{
            font-size: 17px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 22px;
        }}

        .form-group {{ margin-bottom: 16px; }}

        .form-group label {{
            display: block;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 6px;
            letter-spacing: 0.2px;
        }}

        .form-group input {{
            width: 100%;
            padding: 10px 12px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            font-size: 14px;
            color: var(--text-primary);
            transition: var(--transition);
            font-family: inherit;
        }}

        .form-group input::placeholder {{ color: var(--text-muted); }}

        .form-group input:hover {{
            border-color: #CCCCCC;
        }}

        .form-group input:focus {{
            outline: none;
            border-color: var(--accent-auto);
            box-shadow: 0 0 0 3px rgba(122, 104, 85, 0.12);
            background: var(--surface);
        }}

        .modal-btns {{
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 24px;
        }}

        .modal-btn {{
            padding: 9px 20px;
            border-radius: var(--radius-md);
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
            border: 1px solid transparent;
            font-family: inherit;
        }}

        .modal-btn-cancel {{
            background: var(--bg);
            color: var(--text-secondary);
            border-color: var(--border);
        }}
        .modal-btn-cancel:hover {{
            background: var(--surface-hover);
            color: var(--text-primary);
        }}

        .modal-btn-save {{
            background: var(--text-primary);
            color: #FFFFFF;
            border-color: var(--text-primary);
        }}
        .modal-btn-save:hover {{
            background: #444444;
        }}

        @media (max-width: 768px) {{
            body {{ padding: 24px 16px 100px; }}
            .header h1 {{ font-size: 24px; }}
            .calendar-wrapper {{ padding: 16px; }}
            .fab-group {{ bottom: 20px; right: 20px; }}
            .modal {{ align-items: flex-end; }}
            .modal-content {{
                width: 100%;
                max-width: 100%;
                border-radius: var(--radius-xl) var(--radius-xl) 0 0;
                padding: 22px;
            }}
        }}
    </style>
    </head>
    <body>
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
    <a href="cxcalendar://run" class="fab" title="同步学习通">⟳</a>
    <button class="fab" onclick="triggerRestore()" title="恢复备份">⭳</button>
    <button class="fab" onclick="backupData()" title="备份数据">⭱</button>
    <button class="fab" onclick="autoCompleteExpired()" title="归档过期">✓</button>
    <button class="fab main" onclick="openModal()" title="添加任务">+</button>
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
            <label>链接（可选）</label>
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
      });

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
        calendarEl.innerHTML = '';
        var calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: 'dayGridMonth',
          locale: 'zh-cn',
          contentHeight: 'auto',
          dayMaxEvents: false,
          headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: ''
          },
          events: tasks,
          eventContent: function(arg) {
            let props = arg.event.extendedProps;
            let status = props.status || 'todo';
            let source = props.source || 'auto';
            let id = arg.event.id;
            let url = arg.event.url;
            let titleText = arg.event.title;
            let courseText = props.course || '';

            let cardClass = 'task-card ' + source + ' ' + status;
            let sourceIcon = source === 'manual' ? '✎' : '🔗';

            let doneBtn = status === 'done'
                ? `<button class="action-btn" onclick="toggleStatus('${id}', 'todo', event)" title="标记未完成">↩</button>`
                : `<button class="action-btn" onclick="toggleStatus('${id}', 'done', event)" title="标记完成">✓</button>`;
            let editBtn = source === 'manual'
                ? `<button class="action-btn" onclick="editTask('${id}', event)" title="编辑">✎</button>`
                : '';
            let deleteBtn = `<button class="action-btn" onclick="deleteTask('${id}', event)" title="删除">×</button>`;

            let inner =
                '<div class="task-actions">' + doneBtn + editBtn + deleteBtn + '</div>' +
                '<div class="task-header">' +
                  '<span class="task-course" title="' + courseText + '">' + courseText + '</span>' +
                  '<span class="task-badge">' + sourceIcon + '</span>' +
                '</div>' +
                '<div class="task-title" title="' + titleText + '">' + titleText + '</div>' +
                '<div class="task-meta">' + props.deadline_text + '</div>';

            let card = '<div class="' + cardClass + '" title="' + titleText + '">' + inner + '</div>';

            if (url)
                return { html: '<a href="' + url + '" target="_blank" style="text-decoration:none;display:block;" onclick="event.stopPropagation()">' + card + '</a>' };
            return { html: card };
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

      function openModal() { editingId=null; document.querySelectorAll('#addModal input').forEach(i => i.value = ''); document.getElementById('addModal').style.display = 'flex'; }
      function closeModal() { document.getElementById('addModal').style.display = 'none'; }

      function saveManualTask() {
        let course = document.getElementById('mCourse').value.trim() || '自定义';
        let title = document.getElementById('mTitle').value.trim() || '未命名';
        let dInput = document.getElementById('mDate').value;
        let link = document.getElementById('mLink').value.trim();

        let dateObj = dInput ? new Date(dInput) : new Date();
        let dateStr = dInput ? dInput.split('T')[0] : dateObj.toISOString().split('T')[0];
        let displayStr = (dateObj.getMonth()+1) + '月' + dateObj.getDate() + '日';
        if(dInput && dInput.includes('T')) displayStr += ' ' + dateObj.getHours() + ':' + String(dateObj.getMinutes()).padStart(2,'0');

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
            if(idx !== -1) db[idx] = newTask;
        } else {
            db.push(newTask);
        }
        localStorage.setItem('chaoxing_db', JSON.stringify(db));
        closeModal();
        renderCalendar();
      }

      document.getElementById('addModal').addEventListener('click', function(e) {
        if (e.target === this) closeModal();
      });
    </script>
    </body>
    </html>
    '''

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f">>> 网页已生成：{html_path}")
    
    webbrowser.open('file://' + html_path)
    return html_path
