import os
from flask import Flask, request, send_file, jsonify, after_this_request
import yt_dlp

app = Flask(__name__)

# Function to ensure the directory exists
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_audio(url, output_path):
    ensure_directory_exists(os.path.dirname(output_path))
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError:
        # If best audio is not available, download a combined video and audio
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

def download_video(url, output_path, quality):
    ensure_directory_exists(os.path.dirname(output_path))
    
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        'outtmpl': output_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.route('/download/song/<path:video_id>', methods=['GET'])
def download_song(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = f"audio/{video_id}.%(ext)s"
    try:
        download_audio(url, output_path)
        output_file = f"audio/{video_id}.mp3"

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
            except Exception as e:
                app.logger.error(f"Error deleting file {output_file}: {e}")
            return response

        return send_file(output_file, as_attachment=True, attachment_filename=f"{video_id}.mp3")
    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': 'DownloadError', 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'UnexpectedError', 'message': str(e)}), 500

@app.route('/download/video/<path:video_id>', methods=['GET'])
def download_video_route(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = f"video/{video_id}.%(ext)s"
    quality = request.args.get('quality', '480')
    try:
        download_video(url, output_path, quality)
        output_file = f"video/{video_id}.mp4"

        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
            except Exception as e:
                app.logger.error(f"Error deleting file {output_file}: {e}")
            return response

        return send_file(output_file, as_attachment=True, attachment_filename=f"{video_id}.mp4")
    except yt_dlp.utils.DownloadError as e:
        return jsonify({'error': 'DownloadError', 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'UnexpectedError', 'message': str(e)}), 500

if __name__ == '__main__':
    # Ensure the necessary directories exist
    ensure_directory_exists('audio')
    ensure_directory_exists('video')
    
    app.run(host='0.0.0.0', port=8080, debug=True)
