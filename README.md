# 学习通任务管理系统

这是一个基于 Python 的自动作业处理工具，用于自动登录学习通并生成美观的作业日历网页。

## 功能特点

### 🎯 核心功能
- **自动登录学习通**：支持自动识别登录页面并填充账号密码
- **智能爬取任务**：自动获取课程作业信息，包括截止时间和任务详情
- **美观的日历界面**：采用 Apple 极简风格设计，响应式布局，支持深色模式
- **实时同步**：通过自定义协议 `cxcalendar://run` 实现网页内一键同步
- **任务管理**：支持任务状态标记（完成/未完成）、手动添加任务
- **数据管理**：内置数据备份和恢复功能，确保任务数据安全
- **过期任务归档**：自动识别并归档过期任务

### 📋 技术特性
- **跨平台兼容**：支持 Windows 系统
- **智能错误处理**：详细的错误日志记录和提示
- **Edge 浏览器集成**：使用 Microsoft Edge 浏览器进行爬取
- **无侵入式设计**：不修改学习通平台数据

## 快速开始

### 1. 环境准备

确保你的电脑已安装：
- [Python 3.8+](https://www.python.org/)
- [Microsoft Edge 浏览器](https://www.microsoft.com/edge)

### 2. 安装依赖

在项目根目录下打开终端，运行：

```bash
pip install -r requirements.txt
```

### 3. 配置账号信息

编辑 `crawl.py` 文件，填写你的学习通账号和密码：

```python
USERNAME = "你的学习通账号"
PASSWORD = "你的学习通密码"
```

### 4. 运行程序

```bash
python auto_homework.py
```

### 5. 使用生成的网页

程序运行后会自动生成 `my_calendar_final.html` 文件，并在浏览器中打开：

- **查看作业日历**：直接在浏览器中查看所有作业任务
- **同步学习通**：点击页面右下角的「同步学习通」按钮更新数据
- **添加任务**：点击「添加任务」手动添加作业
- **备份数据**：使用「备份数据」功能保存当前任务状态
- **恢复数据**：使用「恢复备份」功能恢复之前的任务状态
- **归档过期**：点击「归档过期」按钮自动标记过期任务为完成

## 浏览器驱动管理

**重要提示**：浏览器驱动版本必须与 Edge 浏览器版本完全一致，否则程序会启动失败！

### 1. 手动管理驱动（推荐，更稳定）

1. **查看 Edge 版本**：浏览器设置 → 关于 Microsoft Edge
   - 示例版本：120.0.2210.133
2. **下载对应驱动**：[Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
   - 确保下载的驱动版本与浏览器版本完全一致
3. **放置驱动文件**：将下载的 `msedgedriver.exe` 放在项目根目录下

### 2. 自动管理驱动（开发环境适用）

- 程序已集成 `webdriver-manager` 支持
- 在开发环境下运行 `python auto_homework.py` 时，会自动下载匹配的驱动
- **注意**：打包成 exe 后，自动驱动管理可能无法正常工作，建议使用手动管理方式

## 自定义协议注册

程序会在首次运行时自动尝试注册自定义协议 `cxcalendar://`，以便在网页中直接调用同步功能。

### 手动注册（如果自动注册失败）

1. 打开命令提示符（管理员权限）
2. 进入项目根目录
3. 运行命令：
   ```bash
   python -c "import winreg, os; exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'auto_homework.exe'); key_path = 'Software\\Classes\\cxcalendar'; with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key: winreg.SetValue(key, '', winreg.REG_SZ, 'URL:cxcalendar Protocol'); winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, ''); with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path + '\\shell\\open\\command') as cmd_key: winreg.SetValue(cmd_key, '', winreg.REG_SZ, f'\"{exe_path}\" \"%1\"')"
   ```
4. 重新打开网页，点击同步按钮即可直接运行 exe 文件

## 打包说明

### 手动打包方式

1. **安装 PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **执行打包命令**
   ```bash
   pyinstaller --onefile --add-data "msedgedriver.exe;." auto_homework.py
   ```

3. **打包后操作**
   - 生成的 exe 文件位于 `dist` 目录下
   - 确保 `msedgedriver.exe` 与 `auto_homework.exe` 在同一目录
   - 首次运行 exe 文件时，可能会弹出安全警告，选择「允许」即可

## 运行说明

### 方式1：直接运行 Python 脚本（开发环境适用）

```bash
python auto_homework.py
```

### 方式2：运行 exe 文件

1. 确保 `msedgedriver.exe` 与 `auto_homework.exe` 在同一目录
2. 双击 `auto_homework.exe` 或在命令行中运行
3. 如果遇到问题，建议使用命令行运行，查看详细错误信息

## 错误处理

程序添加了详细的错误处理机制：
- 命令行模式下会显示详细的错误信息
- 错误信息会保存到 `error.log` 文件中，便于排查问题
- 常见错误会给出明确的解决方案提示

### 常见问题及解决方案

#### 1. 驱动版本不匹配
- **症状**：程序启动失败，提示 "selenium.common.exceptions.SessionNotCreatedException"
- **解决**：更新 `msedgedriver.exe` 到与浏览器完全一致的版本

#### 2. exe 文件无法运行
- **症状**：双击 exe 文件无反应或弹出 "Failed to execute script" 错误
- **解决**：
  - 确保 `msedgedriver.exe` 与浏览器版本一致
  - 确保 `msedgedriver.exe` 与 exe 文件在同一目录
  - 尝试使用命令行运行，查看详细错误信息
  - 检查 Windows 安全中心，确保程序被允许运行

#### 3. 自定义协议无法工作
- **症状**：点击网页同步按钮无反应或弹出黑框后消失
- **解决**：
  - 检查浏览器设置，允许不安全内容
  - 检查 Windows 防火墙设置
  - 尝试直接运行 `auto_homework.exe` 进行同步
  - 运行命令 `python register_protocol.py` 重新注册协议

#### 4. 登录失败
- **症状**：无法自动登录学习通
- **解决**：程序会自动提示手动登录，登录后按回车键继续

## 项目结构

```
ChaoxingCalendar/
├── auto_homework.py      # 主程序入口
├── crawl.py              # 学习通爬取模块
├── ui.py                 # HTML 生成模块
├── msedgedriver.exe      # Edge 浏览器驱动
├── requirements.txt      # 依赖包列表
└── README.md             # 项目说明文档
```

## 技术栈

- **后端**：Python 3.8+
- **爬虫**：Selenium WebDriver
- **前端**：HTML5, CSS3, JavaScript
- **日历组件**：FullCalendar
- **样式**：Apple 极简风格，响应式设计

## 安全注意事项

- **账号安全**：程序会在本地存储你的学习通账号和密码，请确保电脑安全
- **隐私保护**：所有数据均存储在本地，不会上传到任何服务器
- **使用规范**：本工具仅供学习交流使用，请勿用于违反学校或平台规定的行为

## 免责声明

本工具仅供学习交流使用，请勿用于违反学校或平台规定的行为。使用本工具产生的任何后果，由使用者自行承担。

## 更新日志

- **v1.0.0**：初始版本，实现基本功能
  - 自动登录学习通
  - 智能爬取任务
  - 生成美观的日历界面
  - 支持任务管理和数据备份