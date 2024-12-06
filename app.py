import logging
from flask import Flask
from flask_cors import CORS
from routes.webhook import webhook_bp
from utils.statistics_manager import StatisticsManager
import schedule
import time
from threading import Thread
from config import Config

app = Flask(__name__)
CORS(app)

# Регистрация маршрутов
app.register_blueprint(webhook_bp)

# Инициализация статистики
stats_manager = StatisticsManager()

def reset_statistics():
    stats_manager.reset_statistics()

def check_and_reset():
    today = time.localtime()
    if today.tm_mday == 1:
        reset_statistics()

def schedule_monthly_reset():
    # Задача будет запускаться каждый день в 00:00
    schedule.every().day.at("00:00").do(check_and_reset)

    while True:
        schedule.run_pending()
        time.sleep(60)

def start_scheduler():
    scheduler_thread = Thread(target=schedule_monthly_reset)
    scheduler_thread.daemon = True  # Этот поток будет завершаться при закрытии основного приложения
    scheduler_thread.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
    start_scheduler()
    app.run(port=Config.PORT, debug=True)
