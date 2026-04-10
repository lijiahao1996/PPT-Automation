# -*- coding: utf-8 -*-
"""
添加文件日志功能 - 日志写入 C:\Users\50319\Desktop\n8n\logs
"""

with open('C:\\Users\\50319\\Desktop\\n8n\\scripts\\ppt_report_executor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改 _log 方法，添加文件日志
old_log = '''    def _log(self, message: str, level: str = 'INFO'):
        """输出日志（线程安全）"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}<br>"  # 添加 <br> 换行
        # 将日志放入队列（线程安全）
        self.log_queue.put(log_entry)
        # 同时调用回调（如果在主线程中）
        try:
            self.log_callback(log_entry)
        except:
            pass  # 忽略多线程中的 UI 调用错误'''

new_log = '''    def _log(self, message: str, level: str = 'INFO'):
        """输出日志（线程安全）"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        log_entry_html = f"[{timestamp}] [{level}] {message}<br>"  # 添加 <br> 换行用于 Web 显示
        
        # 写入文件日志
        try:
            logs_dir = os.path.join(self.base_dir, 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            log_file = os.path.join(logs_dir, f'ppt_{datetime.now().strftime("%Y%m%d")}.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\\n")
        except Exception as e:
            pass  # 忽略文件写入错误
        
        # 将日志放入队列（线程安全）
        self.log_queue.put(log_entry_html)
        # 同时调用回调（如果在主线程中）
        try:
            self.log_callback(log_entry_html)
        except:
            pass  # 忽略多线程中的 UI 调用错误'''

if old_log in content:
    content = content.replace(old_log, new_log)
    print("Added file logging")
else:
    print("Log method not found")

with open('C:\\Users\\50319\\Desktop\\n8n\\scripts\\ppt_report_executor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
