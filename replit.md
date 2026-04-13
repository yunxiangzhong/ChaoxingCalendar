# 学习通任务管理 (Chaoxing Task Manager)

## Project Overview
A web-based task management calendar for Chaoxing (学习通) students. Displays homework assignments and deadlines in a modern, Apple-style calendar interface. Tasks are stored in browser localStorage and can be manually added, edited, deleted, backed up, and restored.

## Architecture
- **Backend**: Flask (Python) web server (`server.py`) serving the calendar HTML on port 5000
- **Frontend**: Single-page HTML with FullCalendar v6.1.8 and vanilla JavaScript
- **Data Storage**: Browser localStorage (client-side only)
- **Note**: The original Selenium-based Chaoxing scraping (`crawl.py`) is a Windows-only feature and is not used in the web server version

## Key Files
- `server.py` - Flask web server, generates and serves the calendar HTML
- `ui.py` - Original HTML generator (used by main.py for desktop mode)
- `crawl.py` - Selenium-based Chaoxing web scraper (Windows/Edge only)
- `main.py` - Original desktop entry point
- `requirements.txt` - Python dependencies

## Running the App
The app runs via the "Start application" workflow: `python server.py`
- Listens on `0.0.0.0:5000`

## Features
- Monthly calendar view with FullCalendar
- Manual task creation with course name, description, deadline, and optional link
- Task status toggle (todo/done)
- Task deletion and editing (for manual tasks)
- Auto-archive expired tasks
- JSON backup and restore of task data
- Dark mode support via CSS variables
