#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF水印工具 - Web版本
基于Flask的在线水印服务
可部署到Vercel等平台
"""

from flask import Flask, request, send_file, render_template_string, jsonify
import os
import tempfile
import zipfile
from werkzeug.utils import secure_filename
import io
from watermark_tool import WatermarkTool

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB限制

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 PDF水印工具 - 在线版</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Arial', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 40px; }
        .upload-section { 
            border: 3px dashed #667eea; 
            border-radius: 10px; 
            padding: 40px; 
            text-align: center; 
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }
        .upload-section:hover { 
            border-color: #764ba2; 
            background: #f8f9ff; 
        }
        .upload-section h3 { color: #667eea; margin-bottom: 15px; }
        .file-input { 
            margin: 10px 0; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            width: 100%; 
            font-size: 16px;
        }
        .settings { 
            background: #f8f9ff; 
            padding: 25px; 
            border-radius: 10px; 
            margin-bottom: 30px; 
        }
        .settings h3 { color: #667eea; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold; 
            color: #333; 
        }
        .form-group input, .form-group select { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 16px;
        }
        .btn { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 8px; 
            font-size: 18px; 
            cursor: pointer; 
            width: 100%; 
            transition: all 0.3s ease;
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 5px 15px rgba(0,0,0,0.2); 
        }
        .btn:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
            transform: none; 
        }
        .progress { 
            display: none; 
            margin-top: 20px; 
            text-align: center; 
        }
        .progress-bar { 
            background: #f0f0f0; 
            height: 10px; 
            border-radius: 5px; 
            overflow: hidden; 
            margin: 10px 0; 
        }
        .progress-fill { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            height: 100%; 
            width: 0%; 
            transition: width 0.3s ease; 
        }
        .result { 
            display: none; 
            background: #e8f5e8; 
            border: 2px solid #4caf50; 
            border-radius: 10px; 
            padding: 20px; 
            text-align: center; 
            margin-top: 20px; 
        }
        .features { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-top: 30px; 
        }
        .feature { 
            text-align: center; 
            padding: 20px; 
            background: #f8f9ff; 
            border-radius: 10px; 
        }
        .feature h4 { color: #667eea; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 PDF水印工具</h1>
            <p>在线为PDF添加水印 | 支持图片文件夹转PDF</p>
        </div>
        
        <div class="content">
            <form id="watermarkForm" enctype="multipart/form-data">
                <div class="upload-section">
                    <h3>📁 选择文件</h3>
                    <div style="margin-bottom: 20px;">
                        <label>
                            <input type="radio" name="mode" value="pdf" checked> 
                            📄 上传PDF文件
                        </label>
                        <label style="margin-left: 20px;">
                            <input type="radio" name="mode" value="folder"> 
                            📁 上传图片ZIP包
                        </label>
                    </div>
                    <input type="file" id="fileInput" class="file-input" accept=".pdf,.zip" required>
                    <p style="color: #666; margin-top: 10px;">
                        PDF模式：支持PDF文件 | 文件夹模式：支持包含图片的ZIP文件
                    </p>
                </div>
                
                <div class="settings">
                    <h3>🎨 水印设置</h3>
                    <div class="form-group">
                        <label for="watermarkText">水印文字</label>
                        <input type="text" id="watermarkText" name="watermarkText" 
                               value="朋阳托辅内部专用资料" placeholder="输入水印文字">
                    </div>
                    <div class="form-group">
                        <label for="fontSize">字体大小 (px)</label>
                        <input type="range" id="fontSize" name="fontSize" 
                               min="20" max="50" value="32" 
                               oninput="document.getElementById('fontSizeValue').textContent = this.value">
                        <span id="fontSizeValue">32</span> px
                    </div>
                </div>
                
                <button type="submit" class="btn" id="submitBtn">
                    🚀 开始处理
                </button>
            </form>
            
            <div class="progress" id="progress">
                <p>正在处理中，请稍候...</p>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
            </div>
            
            <div class="result" id="result">
                <h3>✅ 处理完成！</h3>
                <p id="resultMessage"></p>
                <a id="downloadLink" class="btn" style="display: inline-block; margin-top: 15px; text-decoration: none;">
                    ⬇️ 下载文件
                </a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h4>🎯 智能布局</h4>
                    <p>根据字体大小自动调整水印密度和位置</p>
                </div>
                <div class="feature">
                    <h4>🔤 中文支持</h4>
                    <p>完美支持中文水印文字显示</p>
                </div>
                <div class="feature">
                    <h4>📱 批量处理</h4>
                    <p>支持大文件和多页面PDF处理</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('watermarkForm');
        const submitBtn = document.getElementById('submitBtn');
        const progress = document.getElementById('progress');
        const result = document.getElementById('result');
        const fileInput = document.getElementById('fileInput');
        const modeRadios = document.querySelectorAll('input[name="mode"]');
        
        // 根据模式切换文件类型
        modeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'pdf') {
                    fileInput.accept = '.pdf';
                } else {
                    fileInput.accept = '.zip';
                }
            });
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const file = fileInput.files[0];
            const mode = document.querySelector('input[name="mode"]:checked').value;
            const watermarkText = document.getElementById('watermarkText').value;
            const fontSize = document.getElementById('fontSize').value;
            
            if (!file) {
                alert('请选择文件');
                return;
            }
            
            formData.append('file', file);
            formData.append('mode', mode);
            formData.append('watermarkText', watermarkText);
            formData.append('fontSize', fontSize);
            
            // 显示进度
            submitBtn.disabled = true;
            progress.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const filename = response.headers.get('Content-Disposition')
                        .split('filename=')[1].replace(/"/g, '');
                    
                    document.getElementById('downloadLink').href = url;
                    document.getElementById('downloadLink').download = filename;
                    document.getElementById('resultMessage').textContent = 
                        `文件处理完成！大小: ${(blob.size / 1024 / 1024).toFixed(2)} MB`;
                    
                    result.style.display = 'block';
                } else {
                    const error = await response.text();
                    alert('处理失败: ' + error);
                }
            } catch (error) {
                alert('上传失败: ' + error.message);
            } finally {
                submitBtn.disabled = false;
                progress.style.display = 'none';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_file():
    """处理上传的文件"""
    try:
        # 获取参数
        mode = request.form.get('mode', 'pdf')
        watermark_text = request.form.get('watermarkText', '朋阳托辅内部专用资料')
        font_size = int(request.form.get('fontSize', 32))
        
        if 'file' not in request.files:
            return '没有上传文件', 400
        
        file = request.files['file']
        if file.filename == '':
            return '没有选择文件', 400
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(input_path)
            
            tool = WatermarkTool()
            
            if mode == 'pdf':
                # PDF模式
                output_path = os.path.join(temp_dir, 'output_watermarked.pdf')
                success = tool.process_pdf_watermark(
                    input_path, output_path, watermark_text, font_size
                )
                output_filename = f"{os.path.splitext(file.filename)[0]}_带水印.pdf"
                
            else:
                # 文件夹模式
                extract_dir = os.path.join(temp_dir, 'extracted')
                os.makedirs(extract_dir)
                
                # 解压ZIP文件
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                output_path = os.path.join(temp_dir, 'output_from_images.pdf')
                success = tool.process_folder_to_pdf(
                    extract_dir, output_path, watermark_text, font_size
                )
                output_filename = f"{os.path.splitext(file.filename)[0]}_带水印.pdf"
            
            if not success:
                return '处理失败', 500
            
            # 返回处理后的文件
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/pdf'
            )
            
    except Exception as e:
        return f'处理出错: {str(e)}', 500

@app.route('/health')
def health():
    """健康检查"""
    return {'status': 'ok', 'message': 'PDF水印工具运行正常'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
