from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF水印工具测试</title>
            <meta charset="UTF-8">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 600px; 
                    margin: 50px auto; 
                    padding: 20px; 
                    background: #f0f8ff;
                    text-align: center;
                }
                .container { 
                    background: white; 
                    padding: 40px; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }
                h1 { color: #2c3e50; margin-bottom: 30px; }
                .status { 
                    background: #d4edda; 
                    color: #155724;
                    padding: 20px; 
                    border-radius: 10px; 
                    margin: 20px 0;
                    border: 1px solid #c3e6cb;
                }
                .info {
                    background: #e7f3ff;
                    color: #0c5460;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 PDF水印工具</h1>
                
                <div class="status">
                    ✅ Vercel服务器连接成功！
                </div>
                
                <div class="info">
                    <strong>测试信息：</strong><br>
                    • 使用Python BaseHTTPRequestHandler<br>
                    • 不依赖Flask框架<br>
                    • 最简单的HTTP服务<br>
                </div>
                
                <p><strong>部署状态：</strong> 正常运行</p>
                <p><strong>服务器时间：</strong> <span id="time"></span></p>
                <p><strong>下一步：</strong> 添加PDF处理功能</p>
            </div>
            
            <script>
                document.getElementById('time').textContent = new Date().toLocaleString();
            </script>
        </body>
        </html>
        '''
        
        self.wfile.write(html.encode('utf-8'))
        return
