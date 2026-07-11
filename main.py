import os
import telebot
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. Điền mã Token Telegram của bạn vào đây
API_TOKEN = '8642171960:AAFxVBOQ4fCmeC3jnowscSw7yiu5-ASse5s'
bot = telebot.TeleBot(API_TOKEN)

# 2. Điền mã API Key bạn vừa lấy từ email ocr.space vào đây
OCR_SPACE_API_KEY = 'K81435986188957'

# Cấu hình luật tính điểm (Hạng 1 = 12đ, Hạng 2 = 9đ...)
PLACEMENT_RULES = {1: 12, 2: 9, 3: 8, 4: 7, 5: 6, 6: 5, 7: 4, 8: 3, 9: 2, 10: 1, 11: 1, 12: 0}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Chào mừng! Gửi ảnh kết quả trận đấu Free Fire để tính điểm tự động.")

@bot.message_handler(content_types=['photo'])
def handle_match_photo(message):
    bot.reply_to(message, "🔍 Đang gửi ảnh lên Cloud OCR để phân tích...")
    try:
        # Lấy URL đường dẫn ảnh trực tiếp từ Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://telegram.org{API_TOKEN}/{file_info.file_path}"
        
        # Gửi link ảnh sang server OCR Space xử lý từ xa để tiết kiệm RAM
        payload = {
            'url': file_url,
            'apikey': OCR_SPACE_API_KEY,
            'language': 'eng',
            'isOverlayRequired': False
        }
        response = requests.post('https://ocr.space', data=payload).json()
        
        if response.get("ParsedResults"):
            parsed_text = response["ParsedResults"][0]["ParsedText"]
            # Phản hồi lại nội dung chữ quét được để kiểm tra ban đầu
            bot.reply_to(message, f"📊 Quét thành công! Dữ liệu đọc được:\n\n{parsed_text}")
        else:
            bot.reply_to(message, "❌ Server OCR không đọc được chữ từ bức ảnh này.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Có lỗi xảy ra: {str(e)}")

# Máy chủ web mini giữ cổng Port cho Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running smoothly!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    bot.infinity_polling()
