# launcher.py
import subprocess
import webbrowser
import time
import socket

p = subprocess.Popen(["python", "D:/p/github/coshair/app.py"])
# 等待端口可用（同上 wait_for_port）
# 打开浏览器
webbrowser.open("http://localhost:5000")
# 可选择 p.wait() 或根据需要退出 launcher 而让 server 继续运行
