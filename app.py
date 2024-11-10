from flask import Flask, render_template, redirect, url_for, request
import youtube_summarizer as yt_summarizer
import youtube_crawler as yt_crawler
import markdown

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    return render_template('main.html')

@app.route('/result', methods=['post','get'])
def summerize():
    if request.method == 'POST':
        yt_url = request.form['yt_link']    
        summary = yt_summarizer.get_summary_parallel(yt_url)
        summary = markdown.markdown(summary)
        title, view_count, published_at, channel_title = yt_crawler.get_video_details(yt_url)

        data = {
            "summary": summary,
            "title": title, 
            "view_count": view_count,
            "published_at": published_at,
            "channel_title": channel_title,
            "video_id": yt_crawler.extract_video_id(yt_url) 
        }
        return render_template('result.html', **data)
    
    else: 
        return redirect('/')


if __name__ == '__main__':
    app.run(port=3000)

