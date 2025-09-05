from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF水印工具 - 测试版</title>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 600px; 
                margin: 50px auto; 
                padding: 20px; 
                background: #f0f0f0;
                text-align: center;
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 10px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .status { 
                background: #e7f3ff; 
                padding: 20px; 
                border-radius: 8px; 
                margin: 20px 0;
            }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
            button {
                background: #007cba;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 PDF水印工具</h1>
            <div class="status success">
                ✅ 基础服务正常运行
            </div>
            
            <p>当前版本：最小测试版</p>
            <p>状态：服务器连接正常</p>
            
            <button onclick="testHealth()">测试健康检查</button>
            <button onclick="testDeps()">测试依赖包</button>
            
            <div id="result" style="margin-top: 20px;"></div>
        </div>
        
        <script>
            async function testHealth() {
                const resultDiv = document.getElementById('result');
                try {
                    const response = await fetch('/health');
                    const data = await response.text();
                    resultDiv.innerHTML = '<div class="status success">健康检查结果: ' + data + '</div>';
                } catch (error) {
                    resultDiv.innerHTML = '<div class="status error">健康检查失败: ' + error.message + '</div>';
                }
            }
            
            async function testDeps() {
                const resultDiv = document.getElementById('result');
                try {
                    const response = await fetch('/test-deps');
                    const data = await response.text();
                    resultDiv.innerHTML = '<div class="status">依赖测试结果: ' + data + '</div>';
                } catch (error) {
                    resultDiv.innerHTML = '<div class="status error">依赖测试失败: ' + error.message + '</div>';
                }
            }
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """健康检查"""
    return 'OK - Flask服务运行正常'

@app.route('/test-deps')
def test_deps():
    """测试依赖包"""
    results = []
    
    # 测试Flask
    try:
        import flask
        results.append(f"✅ Flask {flask.__version__}")
    except ImportError as e:
        results.append(f"❌ Flask导入失败: {e}")
    
    # 测试PyPDF2
    try:
        import PyPDF2
        results.append(f"✅ PyPDF2 {PyPDF2.__version__}")
    except ImportError as e:
        results.append(f"❌ PyPDF2导入失败: {e}")
    
    # 测试Pillow
    try:
        import PIL
        results.append(f"✅ Pillow {PIL.__version__}")
    except ImportError as e:
        results.append(f"❌ Pillow导入失败: {e}")
    
    # 测试ReportLab
    try:
        import reportlab
        results.append(f"✅ ReportLab {reportlab.Version}")
    except ImportError as e:
        results.append(f"❌ ReportLab导入失败: {e}")
    
    return '<br>'.join(results)

# Vercel入口点
def handler(request, context):
    return app(request, context)

if __name__ == '__main__':
    app.run(debug=True)