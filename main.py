import os
import requests
from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip

app = Flask(__name__)

# Токен твого бота, який ти отримав від BotFather
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route('/process-video', methods=['POST'])
def process_video():
    data = request.json
    file_id = data.get("file_id")
    is_shorts = data.get("is_shorts", True) # За замовчуванням робимо Shorts
    
    if not file_id:
        return jsonify({"error": "No file_id provided"}), 400

    try:
        # 1. Отримуємо шлях до файлу в Telegram
        file_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}").json()
        file_path = file_info['result']['file_path']
        video_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        
        # Завантажуємо відео локально на сервер
        local_input = "input_video.mp4"
        local_output = "output_video.mp4"
        
        with requests.get(video_url, stream=True) as r:
            with open(local_input, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # 2. Монтаж відео через MoviePy
        clip = VideoFileClip(local_input)
        
        if is_shorts:
            # Обрізаємо до 59 секунд, якщо воно довше
            if clip.duration > 59:
                clip = clip.subclip(0, 59)
            
            # Робимо вертикальний формат 9:16 (розумний кроп по центру)
            w, h = clip.size
            new_w = int(h * 9 / 16)
            x1 = (w - new_w) // 2
            clip = clip.crop(x1=x1, y1=0, width=new_w, height=h)
        
        # Зберігаємо змонтоване відео
        clip.write_videofile(local_output, codec="libx264", audio_codec="aac")
        clip.close()
        
        return jsonify({"status": "success", "message": "Відео успішно змонтовано!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
