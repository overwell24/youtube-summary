from flask import Flask, render_template, redirect, request
import sys
import os
# 현재 스크립트 위치를 기준으로 services 폴더 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
from services.youtube_api import YouTubeAPI
from services.youtube_summary import YouTubeSummary
import markdown

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    return render_template('main.html')

@app.route('/result', methods=['post','get'])
def summerize():
    if request.method == 'POST':
        youtube_url = request.form['yt_link']
        
        youtube_api = YouTubeAPI()
        youtube_summary = YouTubeSummary(youtube_url, youtube_api)

        summary = youtube_summary.summarize()
        summary = markdown.markdown(summary)
        
        title, view_count, published_at, channel_title = youtube_api.get_youtube_details(youtube_url)

        data = {
            "summary": summary,
            "title": title, 
            "view_count": view_count,
            "published_at": published_at,
            "channel_title": channel_title,
            "video_id": youtube_api.extract_video_id(youtube_url) 
        }
        return render_template('result.html', **data)
    
    else: 
        return redirect('/')


if __name__ == '__main__':
    app.run(port=3000)

