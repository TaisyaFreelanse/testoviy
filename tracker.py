#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отслеживания IP-адресов через случайные ссылки
"""

import random
import string
from flask import Flask, request, jsonify
from datetime import datetime
import threading
import subprocess
import time
import requests
import sys
import os

app = Flask(__name__)

# Хранилище для отслеживания посещений
visits = {}
public_url = None
ngrok_process = None

def generate_random_link(length=20):
    """Генерирует случайную строку для ссылки"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Генерируем случайную ссылку при запуске
tracking_code = generate_random_link()

def get_public_url():
    """Получает публичный URL через ngrok"""
    global public_url, ngrok_process
    
    # Определяем путь к ngrok (сначала проверяем текущую папку)
    ngrok_path = None
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_ngrok = os.path.join(current_dir, 'ngrok.exe')
    
    if os.path.exists(local_ngrok):
        ngrok_path = local_ngrok
        print(f"✅ Найден ngrok.exe в текущей папке")
    else:
        # Пробуем найти в PATH
        ngrok_path = 'ngrok'
    
    try:
        # Проверяем, работает ли ngrok
        result = subprocess.run([ngrok_path, 'version'], 
                              capture_output=True, text=True, timeout=5)
        
        # Запускаем ngrok в фоне
        print("🔄 Запуск ngrok для создания публичной ссылки...")
        ngrok_process = subprocess.Popen(
            [ngrok_path, 'http', '5000', '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        # Пытаемся получить публичный URL через ngrok API с несколькими попытками
        print("⏳ Ожидание готовности ngrok...")
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                time.sleep(2)  # Ждем между попытками
                response = requests.get('http://127.0.0.1:4040/api/tunnels', timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get('tunnels', [])
                    if tunnels:
                        # Ищем HTTPS туннель (предпочтительно) или HTTP
                        https_tunnel = None
                        http_tunnel = None
                        for tunnel in tunnels:
                            url = tunnel.get('public_url', '')
                            if url.startswith('https://'):
                                https_tunnel = url
                            elif url.startswith('http://') and not http_tunnel:
                                http_tunnel = url
                        
                        public_url = https_tunnel or http_tunnel
                        if public_url:
                            print(f"✅ Ngrok успешно запущен!")
                            print(f"🌐 Публичный URL получен: {public_url}")
                            return public_url
            except requests.exceptions.ConnectionError:
                # API еще не готов, продолжаем попытки
                if attempt < max_attempts - 1:
                    continue
            except Exception as e:
                # Другие ошибки
                if attempt == max_attempts - 1:
                    print(f"⚠️  Ошибка при получении URL: {e}")
        
        # Если не удалось получить автоматически
        print("⚠️  Не удалось автоматически получить ngrok URL")
        print("💡 Ngrok запущен, но URL нужно получить вручную:")
        print("   1. Откройте http://127.0.0.1:4040 в браузере")
        print("   2. Скопируйте публичный URL (Forwarding)")
        print("   3. Добавьте /track/" + tracking_code + " к этому URL")
        return None
        
    except FileNotFoundError:
        print("❌ Ngrok не найден!")
        print(f"\n💡 Проверьте наличие ngrok.exe в папке: {current_dir}")
        print("📥 Если его нет, скачайте с https://ngrok.com/download")
        return None
    except Exception as e:
        print(f"⚠️  Ошибка при запуске ngrok: {e}")
        return None

# Пытаемся получить публичный URL
public_url = get_public_url()
if public_url:
    tracking_url = f"{public_url}/track/{tracking_code}"
else:
    # Fallback на localhost, если ngrok не работает
    tracking_url = f"http://localhost:5000/track/{tracking_code}"

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
    
    # Сохраняем информацию о посещении
    visit_info = {
        'ip': ip,
        'timestamp': timestamp,
        'user_agent': user_agent,
        'code': code
    }
    
    visits[code] = visit_info
    
    # Выводим информацию в консоль
    print("\n" + "="*60)
    print("🔍 ОБНАРУЖЕНО ПОСЕЩЕНИЕ!")
    print("="*60)
    print(f"📅 Время: {timestamp}")
    print(f"🌐 IP-адрес: {ip}")
    print(f"🔗 Код ссылки: {code}")
    print(f"💻 Браузер: {user_agent}")
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
    return jsonify({
        'tracking_url': tracking_url,
        'visits': visits
    })

def print_info():
    """Выводит информацию о сгенерированной ссылке"""
    print("\n" + "="*60)
    print("🎯 ТРЕКЕР IP-АДРЕСОВ ЗАПУЩЕН!")
    print("="*60)
    print(f"🔗 Случайная ссылка для друга:")
    print(f"   {tracking_url}")
    print(f"\n📋 Код отслеживания: {tracking_code}")
    print(f"\n💡 Отправьте эту ссылку другу!")
    print(f"💡 Когда он перейдет по ней, здесь появится его IP-адрес")
    if public_url:
        print(f"\n🌐 Публичный URL: {public_url}")
        print(f"🌐 Локальный сервер: http://localhost:5000")
    else:
        print(f"\n⚠️  Используется локальный адрес")
        print(f"💡 Для публичной ссылки установите ngrok")
    print(f"📊 Статус: {public_url or 'http://localhost:5000'}/status")
    print("="*60 + "\n")

def cleanup():
    """Очистка при выходе"""
    global ngrok_process
    if ngrok_process:
        try:
            ngrok_process.terminate()
            ngrok_process.wait(timeout=2)
        except:
            try:
                ngrok_process.kill()
            except:
                pass

if __name__ == '__main__':
    try:
        print_info()
        print("⏳ Ожидание посещений... (Ctrl+C для остановки)\n")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка сервера...")
        cleanup()
        sys.exit(0)

