from flask import Flask, request, send_file, render_template_string
import os
import sys
import tempfile
import zipfile
from werkzeug.utils import secure_filename
import io
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import re
import glob

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB限制

class WatermarkTool:
    def __init__(self):
        self.default_opacity = 0.35
        self.default_rotation = 45
        
    def create_watermark_pdf(self, width, height, watermark_text, font_size):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        
        # 使用默认字体
        font_name = 'Helvetica'
        c.setFont(font_name, font_size)
        c.setFillColor(Color(0, 0, 0, alpha=self.default_opacity))
        
        # 简单布局
        rows, cols = 4, 2
        row_spacing = height / (rows + 1)
        col_spacing = width / (cols + 1)
        
        for row in range(rows):
            for col in range(cols):
                x = col_spacing * (col + 1)
                y = height - row_spacing * (row + 1)
                
                c.saveState()
                c.translate(x, y)
                c.rotate(self.default_rotation)
                
                text_width = c.stringWidth(watermark_text, font_name, font_size)
                c.drawString(-text_width/2, -font_size/2, watermark_text)
                
                c.restoreState()
        
        c.save()
        packet.seek(0)
        return packet

    def add_watermark_to_pdf(self, input_pdf, output_pdf, watermark_text, font_size):
        try:
            reader = PdfReader(input_pdf)
            writer = PdfWriter()
            
            for page in reader.pages:
                page_box = page.mediabox
                page_width = float(page_box.width)
                page_height = float(page_box.height)
                
                watermark_packet = self.create_watermark_pdf(
                    page_width, page_height, watermark_text, font_size
                )
                watermark_reader = PdfReader(watermark_packet)
                watermark_page = watermark_reader.pages[0]
                
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            with open(output_pdf, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF水印工具</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
        h1 { color: #333; text-align: center; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, button { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007cba; color: white; cursor: pointer; font-size: 16px; }
        button:hover { background: #005a87; }
        .result { margin-top: 20px; padding: 15px; background: #d4edda; border-radius: 5px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 PDF水印工具</h1>
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="form-group">
                <label>选择PDF文件:</label>
                <input type="file" id="pdfFile" accept=".pdf" required>
            </div>
            <div class="form-group">
                <label>水印文字:</label>
                <input type="text" id="watermarkText" value="PENYANG TUTOR INTERNAL USE" required>
            </div>
            <div class="form-group">
                <label>字体大小:</label>
                <input type="number" id="fontSize" value="32" min="20" max="50" required>
            </div>
            <button type="submit">添加水印</button>
        </form>
        <div id="result" class="result">
            <p>处理完成！</p>
            <a id="downloadLink" href="#" download>下载带水印的PDF</a>
        </div>
    </div>
    
    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const file = document.getElementById('pdfFile').files[0];
            const watermarkText = document.getElementById('watermarkText').value;
            const fontSize = document.getElementById('fontSize').value;
            
            if (!file) {
                alert('请选择PDF文件');
                return;
            }
            
            formData.append('file', file);
            formData.append('watermarkText', watermarkText);
            formData.append('fontSize', fontSize);
            
            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    document.getElementById('downloadLink').href = url;
                    document.getElementById('downloadLink').download = file.name.replace('.pdf', '_watermarked.pdf');
                    document.getElementById('result').style.display = 'block';
                } else {
                    alert('处理失败');
                }
            } catch (error) {
                alert('上传失败: ' + error.message);
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/process', methods=['POST'])
def process_file():
    try:
        watermark_text = request.form.get('watermarkText', 'PENYANG TUTOR INTERNAL USE')
        font_size = int(request.form.get('fontSize', 32))
        
        if 'file' not in request.files:
            return '没有上传文件', 400
        
        file = request.files['file']
        if file.filename == '':
            return '没有选择文件', 400
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(input_path)
            
            output_path = os.path.join(temp_dir, 'output_watermarked.pdf')
            
            tool = WatermarkTool()
            success = tool.add_watermark_to_pdf(input_path, output_path, watermark_text, font_size)
            
            if not success:
                return '处理失败', 500
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"{os.path.splitext(file.filename)[0]}_watermarked.pdf",
                mimetype='application/pdf'
            )
            
    except Exception as e:
        return f'处理出错: {str(e)}', 500

# Vercel需要的默认导出
def handler(request, context):
    return app(request, context)