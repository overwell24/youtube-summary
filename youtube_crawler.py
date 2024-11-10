from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
import os

api_key = os.getenv('GOOGLE_API_KEY')
if api_key is None:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

youtube = build('youtube', 'v3', developerKey=api_key)

def get_video_details(youtube_url):
    video_id = extract_video_id(youtube_url)
    request = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    )
    response = request.execute()

    # 응답에서 제목과 조회수 추출
    if 'items' in response and response['items']:
        video = response['items'][0]
        title = video['snippet']['title']
        view_count = video['statistics']['viewCount']
        published_at = video['snippet']['publishedAt'][:10]
        channel_title = video['snippet']['channelTitle']

        return title, view_count, published_at, channel_title
    else:
        return None, None

def get_subtitle(youtube_url):
    video_id = extract_video_id(youtube_url)

    # 자막을 가져오기 (한국어)
    subtitle = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])

    # 자막을 텍스트 형식으로 변환
    text_formatter = TextFormatter()
    subtitle_text = text_formatter.format_transcript(subtitle).replace("\n", " ")
    
    return subtitle_text

# 파라미터 추출 함수
def extract_video_id(youtube_url):
    return parse_qs(urlparse(youtube_url).query).get('v', [None])[0]

