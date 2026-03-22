"""
DocMarkdownConverter - 入口文件
"""
import sys
from pathlib import Path

# 确保 converter 模块可导入
sys.path.insert(0, str(Path(__file__).parent))

from ui import main

if __name__ == "__main__":
    main()
