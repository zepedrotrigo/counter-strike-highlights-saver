import os
import glob
from moviepy.editor import VideoFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, file, title):
    request = youtube.videos().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': title,
                'category_id': '22'  # Entertainment
            },
            'status': {
                'privacyStatus': 'private'  # or 'public'
            }
        },
        media_body=MediaFileUpload(file)
    )
    response = request.execute()
    print(f'Uploaded: {response["snippet"]["title"]}')

def main():
    youtube = authenticate()
    # assuming that video numbering is done manually or already implemented
    video_number = 1

    for root, _, files in os.walk('/path/to/parent/folder'):
        for file in files:
            if 'MOVIE' in file:
                video_path = os.path.join(root, file)
                upload_video(youtube, video_path, f'[stattrak #{video_number}] recording every kill from now on')
                video_number += 1

if __name__ == '__main__':
    main()