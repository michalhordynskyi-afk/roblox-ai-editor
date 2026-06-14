
import os
import requests
from flask import Flask, request, jsonify, send_file
from moviepy.editor import VideoFileClip

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route('/process-video', methods=['POST'])
def process_video():
    data = request.json
    file_id = data.get("file_id")
    is_shorts = data.get("is_shorts", True)

    if not file_id:
        return jsonify({"error": "No file_id provided"}), 400

    try:
        # Отримуємо шлях до файлу в Telegram
        file_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}").json()
        file_path = file_info['result']['file_path']
        video_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        
        local_input = "input_video.mp4"
        local_output = "output_video.mp4"
        
        # Завантажуємо відео
        with requests.get(video_url, stream=True) as r:
            with open(local_input, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Монтаж відео
        clip = VideoFileClip(local_input)
        
        if is_shorts:
            if clip.duration > 59:
                clip = clip.subclip(0, 59)
            w, h = clip.size
            new_w = int(h * 9 / 16)
            x1 = (w - new_w) // 2
            clip = clip.crop(x1=x1, y1=0, width=new_w, height=h)
        
        clip.write_videofile(local_output, codec="libx264", audio_codec="aac")
        clip.close()
        
        return jsonify({"status": "success", "message": "Відео готове!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Цей маршрут виправлено: тепер він збігається з Make
@app.route('/download-video', methods=['GET'])
def download_file():
    file_path = 'output_video.mp4'
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "Файл ще не створено"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
