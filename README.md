# Auto Homework 项目

这是一个基于 Python 的自动作业处理工具，用于自动登录学习通并生成作业日历。

## 功能特点
* 自动登录学习通并获取课程作业信息
* 生成美观的作业日历网页
* 支持自定义协议 `cxcalendar://run` 实现网页内同步
* 支持任务状态管理、备份和恢复

## 快速开始

### 1. 环境准备
确保你的电脑已安装：
* [Python 3.8+](https://www.python.org/)
* [Microsoft Edge 浏览器](https://www.microsoft.com/edge)

### 2. 安装依赖
在项目根目录下打开终端，运行：
```bash
pip install -r requirements.txt
```

### 3. 运行程序
```bash
python auto_homework.py
```

### 4. 使用生成的网页
程序运行后会自动生成 `my_calendar_final.html` 文件，你可以：
- 直接在浏览器中打开该文件查看作业日历
- 点击页面右下角的「同步学习通」按钮更新数据
- 点击「添加任务」手动添加作业
- 使用「备份数据」和「恢复数据」功能管理任务

## 注意事项

### 浏览器驱动管理

**重要提示**：浏览器驱动版本必须与 Edge 浏览器版本完全一致，否则程序会启动失败！

#### 1. 手动管理驱动（推荐，更稳定）
1. **查看 Edge 版本**：浏览器设置 → 关于 Microsoft Edge
   - 示例版本：120.0.2210.133
2. **下载对应驱动**：[Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
   - 确保下载的驱动版本与浏览器版本完全一致
3. **放置驱动文件**：将下载的 `msedgedriver.exe` 放在项目根目录下

#### 2. 自动管理驱动（开发环境适用）
- 程序已集成 `webdriver-manager` 支持
- 在开发环境下运行 `python auto_homework.py` 时，会自动下载匹配的驱动
- **注意**：打包成 exe 后，自动驱动管理可能无法正常工作，建议使用手动管理方式

### 常见问题及解决方案

#### 1. 驱动版本不匹配
* **症状**：程序启动失败，提示 "selenium.common.exceptions.SessionNotCreatedException"
* **解决**：更新 `msedgedriver.exe` 到与浏览器完全一致的版本

#### 2. exe 文件无法运行
* **症状**：双击 exe 文件无反应或弹出 "Failed to execute script" 错误
* **解决**：
  - 确保 `msedgedriver.exe` 与浏览器版本一致
  - 确保 `msedgedriver.exe` 与 exe 文件在同一目录
  - 尝试使用命令行运行，查看详细错误信息
  - 检查 Windows 安全中心，确保程序被允许运行

#### 3. 自定义协议无法工作
* **症状**：点击网页同步按钮无反应或弹出黑框后消失
* **解决**：
  - 检查浏览器设置，允许不安全内容
  - 检查 Windows 防火墙设置
  - 尝试直接运行 `auto_homework.exe` 进行同步
  - 运行命令 `python register_protocol.py` 重新注册协议

#### 4. 登录失败
* **症状**：无法自动登录学习通
* **解决**：程序会自动提示手动登录，登录后按回车键继续

### 打包说明

#### 手动打包方式

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

### 浏览器直接启用 exe 文件说明

是的，浏览器直接启用 exe 文件需要修改 Windows 注册表，注册自定义协议 `cxcalendar://`。

#### 自动注册
- 程序会在首次运行时自动尝试注册自定义协议
- 注册成功后，点击网页上的「同步学习通」按钮即可直接运行 exe 文件

#### 手动注册（如果自动注册失败）
1. 打开命令提示符（管理员权限）
2. 进入项目根目录
3. 运行命令：
   ```bash
   python -c "import winreg, os; exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'auto_homework.exe'); key_path = 'Software\\Classes\\cxcalendar'; with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key: winreg.SetValue(key, '', winreg.REG_SZ, 'URL:cxcalendar Protocol'); winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, ''); with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path + '\\shell\\open\\command') as cmd_key: winreg.SetValue(cmd_key, '', winreg.REG_SZ, f'\"{exe_path}\" \"%1\"')"
   ```
4. 重新打开网页，点击同步按钮即可直接运行 exe 文件

### 运行说明

#### 方式1：直接运行 Python 脚本（开发环境适用）
```bash
python auto_homework.py
```

#### 方式2：运行 exe 文件
1. 确保 `msedgedriver.exe` 与 `auto_homework.exe` 在同一目录
2. 双击 `auto_homework.exe` 或在命令行中运行
3. 如果遇到问题，建议使用命令行运行，查看详细错误信息

### 错误处理

程序添加了详细的错误处理机制：
- 命令行模式下会显示详细的错误信息
- 错误信息会保存到 `error.log` 文件中，便于排查问题
- 常见错误会给出明确的解决方案提示

### 免责声明
本工具仅供学习交流使用，请勿用于违反学校或平台规定的行为。