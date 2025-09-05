#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF水印工具 - 完整版
功能：
1. 文件夹图片转PDF并添加水印
2. 现有PDF添加水印
3. 自定义水印文字和字体大小
"""

import os
import re
import sys
import glob
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
import io

class WatermarkTool:
    def __init__(self):
        self.default_watermark_text = "朋阳托辅内部专用资料"
        self.default_font_size = 32
        self.default_opacity = 0.35
        self.default_rotation = 45
        
    def extract_page_number(self, filename):
        """从文件名中提取页码数字"""
        match = re.search(r'页面_(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0

    def create_pdf_from_images(self, image_folder, output_pdf):
        """将图片按页码顺序合并成PDF"""
        print(f"正在扫描图片文件夹: {image_folder}")
        
        # 支持的图片格式
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(image_folder, ext)))
            image_files.extend(glob.glob(os.path.join(image_folder, ext.upper())))
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        if not image_files:
            print("错误：没有找到图片文件")
            return False
        
        # 按页码排序
        image_files.sort(key=lambda x: self.extract_page_number(os.path.basename(x)))
        
        print("开始转换图片为PDF...")
        
        # 转换第一张图片
        first_image = Image.open(image_files[0])
        if first_image.mode != 'RGB':
            first_image = first_image.convert('RGB')
        
        # 准备其他图片
        other_images = []
        for i, img_path in enumerate(image_files[1:], 1):
            if i % 10 == 0:
                print(f"处理第 {i+1} 张图片...")
            
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            other_images.append(img)
        
        # 保存为PDF
        print(f"正在保存PDF文件: {output_pdf}")
        first_image.save(
            output_pdf,
            save_all=True,
            append_images=other_images,
            format='PDF'
        )
        
        print(f"✅ PDF创建成功！包含 {len(image_files)} 页")
        return True

    def create_watermark_pdf(self, width, height, watermark_text, font_size):
        """创建水印PDF"""
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        
        # 注册中文字体
        font_name = 'Helvetica'
        try:
            chinese_fonts = [
                '/System/Library/Fonts/STHeiti Light.ttc',
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/Hiragino Sans GB.ttc'
            ]
            
            for font_path in chinese_fonts:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        font_name = 'ChineseFont'
                        break
                    except:
                        continue
        except:
            pass
        
        # 如果没有中文字体，使用英文替代
        if font_name == 'Helvetica':
            watermark_text = "PENYANG TUTOR INTERNAL USE ONLY"
        
        # 设置字体
        c.setFont(font_name, font_size)
        c.setFillColor(Color(0, 0, 0, alpha=self.default_opacity))
        
        # 根据字体大小调整布局密度
        if font_size <= 24:
            rows, cols = 6, 2  # 小字体，密集布局
        elif font_size <= 32:
            rows, cols = 5, 2  # 中等字体
        elif font_size <= 40:
            rows, cols = 4, 2  # 大字体
        else:
            rows, cols = 3, 2  # 超大字体，稀疏布局
        
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
        """为PDF添加水印"""
        try:
            reader = PdfReader(input_pdf)
            writer = PdfWriter()
            
            print(f"正在为PDF添加水印，总页数: {len(reader.pages)}")
            print(f"水印设置 - 文字: {watermark_text}, 字体大小: {font_size}px")
            
            for page_num, page in enumerate(reader.pages):
                if page_num % 20 == 0:
                    print(f"添加水印到第 {page_num + 1} 页...")
                
                # 获取页面尺寸
                page_box = page.mediabox
                page_width = float(page_box.width)
                page_height = float(page_box.height)
                
                # 创建水印
                watermark_packet = self.create_watermark_pdf(
                    page_width, page_height, watermark_text, font_size
                )
                watermark_reader = PdfReader(watermark_packet)
                watermark_page = watermark_reader.pages[0]
                
                # 合并水印
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            # 保存结果
            with open(output_pdf, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"✅ 水印添加完成！")
            return True
            
        except Exception as e:
            print(f"添加水印时出错: {e}")
            return False

    def process_folder_to_pdf(self, folder_path, output_path, watermark_text=None, font_size=None):
        """处理文件夹：图片转PDF并添加水印"""
        if watermark_text is None:
            watermark_text = self.default_watermark_text
        if font_size is None:
            font_size = self.default_font_size
            
        print("=" * 70)
        print("📁 文件夹图片转PDF并添加水印")
        print("=" * 70)
        
        # 检查输入文件夹
        if not os.path.exists(folder_path):
            print(f"❌ 错误：找不到文件夹 {folder_path}")
            return False
        
        # 生成临时PDF文件名
        temp_pdf = output_path.replace('.pdf', '_临时.pdf')
        
        try:
            # 步骤1：图片转PDF
            print("\n📸 步骤1: 将图片按页码顺序合并为PDF")
            if not self.create_pdf_from_images(folder_path, temp_pdf):
                return False
            
            # 步骤2：添加水印
            print(f"\n🏷️  步骤2: 添加水印 (字体大小: {font_size}px)")
            if not self.add_watermark_to_pdf(temp_pdf, output_path, watermark_text, font_size):
                return False
            
            # 步骤3：清理临时文件
            print("\n🧹 步骤3: 清理临时文件")
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
                print("临时文件已删除")
            
            # 显示结果
            self.show_result(output_path, watermark_text, font_size)
            return True
            
        except Exception as e:
            print(f"❌ 处理过程中出错: {e}")
            return False

    def process_pdf_watermark(self, input_pdf, output_pdf, watermark_text=None, font_size=None):
        """处理PDF：为现有PDF添加水印"""
        if watermark_text is None:
            watermark_text = self.default_watermark_text
        if font_size is None:
            font_size = self.default_font_size
            
        print("=" * 70)
        print("📄 PDF文件添加水印")
        print("=" * 70)
        
        # 检查输入文件
        if not os.path.exists(input_pdf):
            print(f"❌ 错误：找不到PDF文件 {input_pdf}")
            return False
        
        try:
            # 添加水印
            print(f"\n🏷️  添加水印 (字体大小: {font_size}px)")
            if not self.add_watermark_to_pdf(input_pdf, output_pdf, watermark_text, font_size):
                return False
            
            # 显示结果
            self.show_result(output_pdf, watermark_text, font_size)
            return True
            
        except Exception as e:
            print(f"❌ 处理过程中出错: {e}")
            return False

    def show_result(self, output_path, watermark_text, font_size):
        """显示处理结果"""
        print("\n" + "=" * 70)
        print("✅ 处理完成！")
        print(f"📄 输出文件: {output_path}")
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"💾 文件大小: {file_size / 1024 / 1024:.2f} MB")
        
        print(f"\n🏷️  水印设置:")
        print(f"   • 文字内容: {watermark_text}")
        print(f"   • 字体大小: {font_size}px")
        print(f"   • 透明度: {int(self.default_opacity * 100)}%")
        print(f"   • 旋转角度: {self.default_rotation}°")
        print("=" * 70)

def show_usage():
    """显示使用说明"""
    print("=" * 80)
    print("🔧 PDF水印工具 - 使用说明")
    print("=" * 80)
    print()
    print("📋 支持的功能:")
    print("   1️⃣  文件夹图片转PDF并添加水印")
    print("   2️⃣  现有PDF文件添加水印")
    print()
    print("🚀 使用方法:")
    print("   python3 watermark_tool.py [模式] [输入路径] [输出路径] [水印文字] [字体大小]")
    print()
    print("📝 参数说明:")
    print("   模式:")
    print("     folder  - 处理图片文件夹")
    print("     pdf     - 处理PDF文件")
    print("   输入路径  - 图片文件夹路径或PDF文件路径")
    print("   输出路径  - 输出PDF文件路径")
    print("   水印文字  - 水印文字内容 (可选，默认: 朋阳托辅内部专用资料)")
    print("   字体大小  - 水印字体大小 (可选，默认: 32)")
    print()
    print("💡 使用示例:")
    print("   # 文件夹转PDF加水印")
    print("   python3 watermark_tool.py folder /path/to/images /path/output.pdf")
    print("   python3 watermark_tool.py folder /path/to/images /path/output.pdf \"自定义水印\" 40")
    print()
    print("   # PDF加水印")
    print("   python3 watermark_tool.py pdf /path/input.pdf /path/output.pdf")
    print("   python3 watermark_tool.py pdf /path/input.pdf /path/output.pdf \"自定义水印\" 24")
    print()
    print("🎨 字体大小建议:")
    print("   • 20-24px: 小字体，密集布局")
    print("   • 28-32px: 标准字体，平衡布局")
    print("   • 36-40px: 大字体，清晰可见")
    print("   • 44px+:   超大字体，稀疏布局")
    print("=" * 80)

def main():
    """主程序"""
    tool = WatermarkTool()
    
    # 检查参数
    if len(sys.argv) < 4:
        show_usage()
        return
    
    mode = sys.argv[1].lower()
    input_path = sys.argv[2]
    output_path = sys.argv[3]
    
    # 可选参数
    watermark_text = sys.argv[4] if len(sys.argv) > 4 else None
    font_size = int(sys.argv[5]) if len(sys.argv) > 5 else None
    
    # 根据模式执行相应功能
    if mode == 'folder':
        success = tool.process_folder_to_pdf(input_path, output_path, watermark_text, font_size)
    elif mode == 'pdf':
        success = tool.process_pdf_watermark(input_path, output_path, watermark_text, font_size)
    else:
        print("❌ 错误：不支持的模式，请使用 'folder' 或 'pdf'")
        show_usage()
        return
    
    if success:
        print("\n🎉 任务执行成功！")
    else:
        print("\n❌ 任务执行失败！")

if __name__ == "__main__":
    main()
