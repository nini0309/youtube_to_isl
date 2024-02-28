from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(youtube_url):
    # Extract video ID from the YouTube URL using regex
    video_id_match = re.search(r'(?<=v=)[^&]+', youtube_url)
    if video_id_match:
        video_id = video_id_match.group(0)
        return video_id
    else:
        return None

def clean_text(text):
    # Remove emojis and special characters using regex
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    return cleaned_text

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        print(transcript)
        text = ""
        for entry in transcript:
            text += entry['text'] + ' '
        return text
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

def get_text(youtube_url: str):

    video_id = extract_video_id(youtube_url)

    if video_id:
        # Fetch and display the transcript
        transcript_text = get_youtube_transcript(video_id)
        if transcript_text:
            print(transcript_text)
            return clean_text(transcript_text)
        else:
            print("Failed to fetch transcript.")
    else:
        print("Invalid YouTube link. Make sure to paste the full URL.")