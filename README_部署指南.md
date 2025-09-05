# 🚀 PDF水印工具 - 部署指南

## 📋 项目结构

```
pdf-watermark-tool/
├── watermark_tool.py          # 核心工具类
├── web_watermark_app.py       # Flask Web应用
├── api/
│   └── index.py              # Vercel API入口
├── requirements.txt           # Python依赖
├── vercel.json               # Vercel配置
├── README_水印工具.md         # 功能说明
└── README_部署指南.md         # 本文档
```

## 🌐 部署方案对比

### 方案1: Vercel部署 (推荐) ⭐

**优势:**
- ✅ 免费额度充足
- ✅ 自动HTTPS
- ✅ 全球CDN加速
- ✅ GitHub集成，自动部署
- ✅ 支持Python

**限制:**
- ⚠️ 单次请求最大10MB
- ⚠️ 函数执行时间限制60秒
- ⚠️ 内存限制1GB

### 方案2: Railway部署

**优势:**
- ✅ 更大的文件处理能力
- ✅ 更长的执行时间
- ✅ 持久化存储

**限制:**
- 💰 免费额度有限

### 方案3: Heroku部署

**优势:**
- ✅ 成熟稳定
- ✅ 丰富的插件生态

**限制:**
- 💰 免费计划已取消

## 🔧 Vercel部署步骤

### 1. 准备GitHub仓库

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit: PDF水印工具"

# 推送到GitHub
git remote add origin https://github.com/你的用户名/pdf-watermark-tool.git
git push -u origin main
```

### 2. Vercel部署配置

1. **访问** [vercel.com](https://vercel.com)
2. **登录** 并连接GitHub账号
3. **导入项目** - 选择你的GitHub仓库
4. **配置设置**:
   - Framework Preset: `Other`
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: 留空
   - Install Command: `pip install -r requirements.txt`

### 3. 环境变量设置

在Vercel项目设置中添加：
```
PYTHONPATH=.
```

### 4. 部署完成

部署成功后，你会得到一个类似这样的URL：
```
https://your-project-name.vercel.app
```

## 🧪 本地测试

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行开发服务器
```bash
python web_watermark_app.py
```

访问: http://localhost:5000

## 🎯 Web版功能特点

### 🖼️ 用户界面
- **现代化设计** - 渐变背景，圆角卡片
- **响应式布局** - 支持手机、平板、桌面
- **拖拽上传** - 直观的文件上传体验
- **实时预览** - 字体大小实时调整

### 📁 文件处理
- **PDF模式** - 直接上传PDF文件添加水印
- **文件夹模式** - 上传ZIP包，自动解压处理图片
- **智能识别** - 自动识别文件类型和页码排序

### ⚙️ 水印设置
- **自定义文字** - 支持中文水印文字
- **字体大小** - 20px-50px滑块调整
- **智能布局** - 根据字体大小自动调整密度
- **预设样式** - 45°旋转，35%透明度

### 📊 处理能力
- **文件大小限制** - 单文件最大100MB
- **批量处理** - 支持多页PDF和多图片ZIP
- **格式支持** - PDF, JPG, PNG, BMP, TIFF

## 🔒 安全考虑

### 文件安全
- **临时存储** - 文件处理完成后自动删除
- **无持久化** - 不在服务器永久保存用户文件
- **内存处理** - 尽可能在内存中完成操作

### 访问控制
- **文件大小限制** - 防止服务器过载
- **处理时间限制** - 避免长时间占用资源
- **错误处理** - 完善的异常捕获和用户提示

## 🎨 界面定制

### 修改样式
编辑 `web_watermark_app.py` 中的 `HTML_TEMPLATE` 部分：

```python
# 修改主题色
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

# 修改按钮样式
.btn { 
    background: linear-gradient(45deg, #667eea, #764ba2); 
}
```

### 添加功能
在Flask路由中添加新的API端点：

```python
@app.route('/api/custom-feature', methods=['POST'])
def custom_feature():
    # 你的自定义功能
    pass
```

## 📈 性能优化

### 前端优化
- **文件压缩** - 压缩CSS和JavaScript
- **懒加载** - 按需加载组件
- **缓存策略** - 合理设置缓存头

### 后端优化
- **内存管理** - 及时释放大文件内存
- **异步处理** - 考虑使用异步框架
- **错误重试** - 处理网络不稳定情况

## 🐛 常见问题

### Q: 文件上传失败
A: 检查文件大小是否超过100MB限制

### Q: 处理时间过长
A: Vercel有60秒执行时间限制，大文件可能超时

### Q: 中文水印显示异常
A: 确保服务器支持中文字体，或使用英文替代

### Q: 部署后访问404
A: 检查vercel.json配置和路由设置

## 🔄 更新部署

### 自动部署
推送到GitHub main分支会自动触发Vercel重新部署：

```bash
git add .
git commit -m "更新功能"
git push origin main
```

### 手动部署
在Vercel控制台点击"Redeploy"按钮

## 📞 技术支持

- **GitHub Issues** - 报告bug和功能请求
- **文档更新** - 持续完善使用说明
- **版本管理** - 使用Git标签管理版本

---

## 🎉 总结

现在你有了两个版本的PDF水印工具：

1. **🖥️ 本地版本** (`watermark_tool.py`) - 命令行工具，功能强大
2. **🌐 Web版本** (`web_watermark_app.py`) - 在线服务，用户友好

选择适合你需求的版本，或者两个都部署！
