import os
import telebot
import easyocr
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. Điền mã Token Telegram của bạn vào đây
API_TOKEN = '8642171960:AAFxVBOQ4fCmeC3jnowscSw7yiu5-ASse5s'
bot = telebot.TeleBot(API_TOKEN)

# Khởi tạo bộ quét ảnh AI
reader = easyocr.Reader(['en'])

# Cấu hình luật tính điểm (Hạng 1 = 12đ, Hạng 2 = 9đ...)
PLACEMENT_RULES = {1: 12, 2: 9, 3: 8, 4: 7, 5: 6, 6: 5, 7: 4, 8: 3, 9: 2, 10: 1, 11: 1, 12: 0}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Chào mừng! Gửi ảnh kết quả để tính điểm tự động.")

@bot.message_handler(content_types=['photo'])
def handle_match_photo(message):
    bot.reply_to(message, "🔍 AI đang phân tích ảnh chụp màn hình kết quả...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_path = "result.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        results = reader.readtext(image_path)
        bot.reply_to(message, "📊 OCR Thành công! Đang xử lý dữ liệu trận đấu...")
    except Exception as e:
        bot.reply_to(message, f"❌ Có lỗi xảy ra: {str(e)}")

# Tạo web server mini để "đánh lừa" Render không bị lỗi Port
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == '__main__':
    # Chạy Web Server ở một luồng riêng
    threading.Thread(target=run_web_server, daemon=True).start()
    # Chạy Bot Telegram
    bot.infinity_polling()
