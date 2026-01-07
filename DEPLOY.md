# Инструкция по деплою на Render

## Вариант 1: Через GitHub (рекомендуется)

1. Создайте репозиторий на GitHub
2. Загрузите код:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/ВАШ_USERNAME/ip-tracker.git
git push -u origin main
```

3. Затем используйте MCP для создания сервиса на Render с указанием репозитория

## Вариант 2: Прямой деплой через Render Dashboard

1. Зайдите на https://dashboard.render.com
2. Нажмите "New +" -> "Web Service"
3. Подключите ваш GitHub репозиторий
4. Настройки:
   - Name: ip-tracker
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. Нажмите "Create Web Service"

После деплоя вы получите публичный URL вида: `https://ip-tracker.onrender.com`

