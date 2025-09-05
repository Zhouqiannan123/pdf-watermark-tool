from flask import Flask, request, send_file, jsonify
import os
import tempfile
from werkzeug.utils import secure_filename
import io

try:
    from PyPDF2 import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import Color
    DEPS_AVAILABLE = True
except ImportError as e:
    DEPS_AVAILABLE = False
    IMPORT_ERROR = str(e)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB限制

# 简单的HTML页面
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF水印工具</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 600px; 
            margin: 50px auto; 
            padding: 20px; 
            background: #f5f5f5;
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            text-align: center; 
            margin-bottom: 30px;
        }
        .form-group { 
            margin: 20px 0; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold; 
            color: #555;
        }
        input, button { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 6px; 
            font-size: 16px;
            box-sizing: border-box;
        }
        button { 
            background: #4CAF50; 
            color: white; 
            border: none;
            cursor: pointer; 
            margin-top: 10px;
        }
        button:hover { 
            background: #45a049; 
        }
        button:disabled { 
            background: #ccc; 
            cursor: not-allowed; 
        }
        .status { 
            margin-top: 20px; 
            padding: 15px; 
            border-radius: 6px; 
            display: none;
        }
        .success { 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb;
        }
        .error { 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb;
        }
        .info {
            background: #e7f3ff;
            color: #0c5460;
            border: 1px solid #b3d7ff;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 PDF水印工具</h1>
        
        <div class="info">
            <strong>功能说明：</strong>
            <ul>
                <li>上传PDF文件，自动添加水印</li>
                <li>支持自定义水印文字</li>
                <li>文件大小限制：10MB</li>
            </ul>
        </div>
        
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="form-group">
                <label>选择PDF文件：</label>
                <input type="file" id="pdfFile" accept=".pdf" required>
            </div>
            
            <div class="form-group">
                <label>水印文字：</label>
                <input type="text" id="watermarkText" value="PENYANG TUTOR INTERNAL USE" required>
            </div>
            
            <div class="form-group">
                <label>字体大小：</label>
                <input type="number" id="fontSize" value="24" min="16" max="40" required>
            </div>
            
            <button type="submit" id="submitBtn">🚀 添加水印</button>
        </form>
        
        <div id="status" class="status"></div>
        
        <div id="result" style="display: none; margin-top: 20px;">
            <a id="downloadLink" href="#" download style="
                display: inline-block; 
                background: #007cba; 
                color: white; 
                padding: 12px 24px; 
                text-decoration: none; 
                border-radius: 6px;
                font-weight: bold;
            ">📥 下载带水印的PDF</a>
        </div>
    </div>
    
    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const statusDiv = document.getElementById('status');
            const submitBtn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            
            // 获取表单数据
            const file = document.getElementById('pdfFile').files[0];
            const watermarkText = document.getElementById('watermarkText').value;
            const fontSize = document.getElementById('fontSize').value;
            
            if (!file) {
                statusDiv.className = 'status error';
                statusDiv.textContent = '请选择PDF文件';
                statusDiv.style.display = 'block';
                return;
            }
            
            // 检查文件大小
            if (file.size > 10 * 1024 * 1024) {
                statusDiv.className = 'status error';
                statusDiv.textContent = '文件大小不能超过10MB';
                statusDiv.style.display = 'block';
                return;
            }
            
            // 准备上传
            const formData = new FormData();
            formData.append('file', file);
            formData.append('watermarkText', watermarkText);
            formData.append('fontSize', fontSize);
            
            // 显示处理状态
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ 处理中...';
            statusDiv.className = 'status info';
            statusDiv.textContent = '正在处理PDF，请稍候...';
            statusDiv.style.display = 'block';
            resultDiv.style.display = 'none';
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    
                    document.getElementById('downloadLink').href = url;
                    document.getElementById('downloadLink').download = 
                        file.name.replace('.pdf', '_watermarked.pdf');
                    
                    statusDiv.className = 'status success';
                    statusDiv.textContent = '✅ 处理完成！文件大小: ' + 
                        (blob.size / 1024 / 1024).toFixed(2) + ' MB';
                    resultDiv.style.display = 'block';
                    
                } else {
                    const errorText = await response.text();
                    statusDiv.className = 'status error';
                    statusDiv.textContent = '❌ 处理失败: ' + errorText;
                }
                
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = '❌ 网络错误: ' + error.message;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 添加水印';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """主页"""
    return HTML_PAGE

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'dependencies': DEPS_AVAILABLE,
        'error': IMPORT_ERROR if not DEPS_AVAILABLE else None
    })

@app.route('/process', methods=['POST'])
def process_file():
    """处理PDF文件"""
    try:
        # 检查依赖
        if not DEPS_AVAILABLE:
            return f'依赖包加载失败: {IMPORT_ERROR}', 500
        
        # 获取参数
        watermark_text = request.form.get('watermarkText', 'PENYANG TUTOR INTERNAL USE')
        font_size = int(request.form.get('fontSize', 24))
        
        # 检查文件
        if 'file' not in request.files:
            return '没有上传文件', 400
        
        file = request.files['file']
        if file.filename == '':
            return '没有选择文件', 400
        
        if not file.filename.lower().endswith('.pdf'):
            return '只支持PDF文件', 400
        
        # 创建临时目录处理文件
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存上传的文件
            input_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(input_path)
            
            # 处理PDF
            output_path = os.path.join(temp_dir, 'output.pdf')
            success = add_watermark_simple(input_path, output_path, watermark_text, font_size)
            
            if not success:
                return '处理PDF时出错', 500
            
            # 返回处理后的文件
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"{os.path.splitext(file.filename)[0]}_watermarked.pdf",
                mimetype='application/pdf'
            )
            
    except Exception as e:
        return f'服务器错误: {str(e)}', 500

def add_watermark_simple(input_pdf, output_pdf, watermark_text, font_size):
    """简化版水印添加功能"""
    try:
        # 读取PDF
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        # 处理每一页
        for page in reader.pages:
            # 获取页面尺寸
            page_box = page.mediabox
            page_width = float(page_box.width)
            page_height = float(page_box.height)
            
            # 创建水印
            watermark_packet = create_simple_watermark(
                page_width, page_height, watermark_text, font_size
            )
            
            if watermark_packet:
                watermark_reader = PdfReader(watermark_packet)
                watermark_page = watermark_reader.pages[0]
                page.merge_page(watermark_page)
            
            writer.add_page(page)
        
        # 保存文件
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)
        
        return True
        
    except Exception as e:
        print(f"水印处理错误: {e}")
        return False

def create_simple_watermark(width, height, text, font_size):
    """创建简单水印"""
    try:
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        
        # 使用默认字体
        c.setFont('Helvetica', font_size)
        c.setFillColor(Color(0, 0, 0, alpha=0.3))  # 30%透明度
        
        # 简单的3x2布局
        rows, cols = 3, 2
        for row in range(rows):
            for col in range(cols):
                x = width * (col + 1) / (cols + 1)
                y = height * (row + 1) / (rows + 1)
                
                c.saveState()
                c.translate(x, y)
                c.rotate(45)  # 45度旋转
                
                # 居中绘制文字
                text_width = c.stringWidth(text, 'Helvetica', font_size)
                c.drawString(-text_width/2, -font_size/2, text)
                
                c.restoreState()
        
        c.save()
        packet.seek(0)
        return packet
        
    except Exception as e:
        print(f"创建水印错误: {e}")
        return None

# Vercel入口点
def handler(request, context):
    return app(request, context)

if __name__ == '__main__':
    app.run(debug=True)