from flask import Flask, request, send_file
import yt_dlp
import os

app = Flask(__name__)

def download_audio(url, output_path):
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': output_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_video(url, output_path):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.route('/download/song/<path:video_id>', methods=['GET'])
def download_song(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = f"downloads/{video_id}.%(ext)s"
    download_audio(url, output_path)
    return send_file(output_path, as_attachment=True)

@app.route('/download/video/<path:video_id>', methods=['GET'])
def download_video_route(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = f"downloads/{video_id}.mp4"
    download_video(url, output_path)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(host='0.0.0.0', port=5000, debug=True)
