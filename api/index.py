#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel API入口文件 - 简化版
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入主应用
from app import app

# Vercel需要的默认导出
def handler(request, response):
    return app.wsgi_app(request.environ, response)

# 或者更简单的方式
app = app