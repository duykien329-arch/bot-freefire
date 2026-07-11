import os
import telebot
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. Điền mã Token Telegram của bạn vào đây
API_TOKEN = '8642171960:AAErXWxh_C1HPfvq7l5B-_4z5vPBsCOUMNE'
bot = telebot.TeleBot(API_TOKEN)

# 2. Điền mã API Key bạn lấy từ email ocr.space vào đây
OCR_SPACE_API_KEY = 'K81435986188957'

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Chào mừng! Gửi ảnh kết quả trận đấu Free Fire để tính điểm tự động.")

@bot.message_handler(content_types=['photo'])
def handle_match_photo(message):
    bot.reply_to(message, "🔍 Đang tải ảnh xuống và gửi lên Cloud OCR để phân tích...")
    try:
        # Tải trực tiếp file ảnh về máy chủ Render trước
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_path = "temp_result.jpg"
        with open(image_path, 'wb') as f:
            f.write(downloaded_file)
            
        # Gửi file ảnh vật lý lên OCR Space dưới dạng multipart/form-data
        payload = {
            'apikey': OCR_SPACE_API_KEY,
            'language': 'eng',
            'isOverlayRequired': False
        }
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('https://ocr.space', data=payload, files=files).json()
            
        # Xóa file tạm sau khi gửi xong để sạch máy chủ
        if os.path.exists(image_path):
            os.remove(image_path)
            
        if response.get("ParsedResults"):
            parsed_text = response["ParsedResults"][0]["ParsedText"]
            if parsed_text.strip():
                bot.reply_to(message, f"📊 Quét thành công! Dữ liệu chữ đọc được:\n\n{parsed_text}")
            else:
                bot.reply_to(message, "⚠️ AI không tìm thấy chữ nào trong bức ảnh này.")
        else:
            bot.reply_to(message, f"❌ Lỗi từ Server OCR: {response.get('ErrorMessage', ['Không rõ nguyên nhân'])[0]}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Có lỗi nội bộ xảy ra: {str(e)}")

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
