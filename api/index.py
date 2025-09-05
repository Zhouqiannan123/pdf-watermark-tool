#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel API入口文件
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_watermark_app import app

# Vercel需要的handler
def handler(request):
    return app(request)

# 如果直接运行，启动开发服务器
if __name__ == "__main__":
    app.run(debug=True)
