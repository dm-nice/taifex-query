import sys
import os

# 將專案根目錄加入 sys.path，這樣測試程式才能找到 config.py 和 modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
