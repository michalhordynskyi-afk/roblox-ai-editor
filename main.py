
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
