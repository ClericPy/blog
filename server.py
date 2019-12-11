import os
import webbrowser
from threading import Timer

url = 'http://127.0.0.1:1313/blog/'
os.system('hugo')
Timer(1, lambda: webbrowser.open(url)).start()
os.system('hugo server')
