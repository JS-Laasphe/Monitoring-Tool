# Programm zum Testen der Internetverbindung. Bei Ausführung wird ein Speedtest durchgeführt und das Ergebnis
# protokolliert. Zusätzlich wird der Standort abgefragt, falls ein VPN getestet wird und eine Nachricht via Telegram
# versendet. Die Funktionen können einzeln aktiviert/deaktiviert werden.
# Erstellt werden ein internet_speed-Log sowie ein error-Log.

import logging
from logging.handlers import RotatingFileHandler
import speedtest
import requests
from telegram import Bot

# Einstellungen:
perform_speedtest = True
get_location_info = True
write_logs = True
send_telegram_messages = False

info_handler = RotatingFileHandler("internet_speed.log", maxBytes=1000000, backupCount=5)
error_handler = RotatingFileHandler("error.log", maxBytes=1000000, backupCount=5)
info_logger = logging.getLogger("InfoLogger")
info_logger.setLevel(logging.INFO)
info_logger.addHandler(info_handler)
error_logger = logging.getLogger("ErrorLogger")
error_logger.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)

bot_token = "your_bot_token"
chat_id = "your_chat_id"


def get_bot():
    if send_telegram_messages:
        try:
            return Bot(token=bot_token)
        except Exception as e:
            if write_logs:
                error_logger.error("Error in get_bot: " + str(e))
            return None
    else:
        return None


bot = get_bot()


def get_speed():
    if perform_speedtest:
        try:
            s = speedtest.Speedtest()
            s.get_best_server()
            ping_time = s.results.ping
            download_speed = round(s.download() / 10 ** 6 / 8, 2)  # in MBps, rounded to 2 decimals
            upload_speed = round(s.upload() / 10 ** 6 / 8, 2)  # in MBps, rounded to 2 decimals
            return download_speed, upload_speed, ping_time
        except Exception as e:
            if write_logs:
                error_logger.error("Error in get_speed: " + str(e))
            return None, None, None
    else:
        return None, None, None


def get_location():
    if get_location_info:
        try:
            r = requests.get("https://ipinfo.io/")
            return r.json()
        except Exception as e:
            if write_logs:
                error_logger.error("Error in get_location: " + str(e))
            return None
    else:
        return None


def send_telegram_message(message):
    if send_telegram_messages and bot is not None:
        try:
            bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            if write_logs:
                error_logger.error("Error in send_telegram_message: " + str(e))


if __name__ == "__main__":
    download_speed, upload_speed, ping_time = get_speed()
    location_info = get_location()
    if download_speed is not None and upload_speed is not None and ping_time is not None and location_info is not None:
        message = f"Download Geschwindigkeit: {download_speed} MBps, Upload Geschwindigkeit: {upload_speed} MBps, Ping Zeit: {ping_time} ms, Standort: {location_info['city']}, {location_info['region']}, {location_info['country']}"
        if write_logs:
            info_logger.info(message)
        send_telegram_message(message)
    else:
        if write_logs:
            error_logger.error("Could not perform speed test or fetch location info")
