from __future__ import print_function
import pickle
import os.path
import pprint

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
pp = pprint.PrettyPrinter(indent=4)

def download_file(file_id):
    service = get_service()
    return service.files().get_media(fileId=file_id)

def get_service():
    creds = None
    """Файл token.pickle хранит токены доступа пользователя и обновляет его и является
    создается автоматически при завершении потока авторизации для первого
    время"""
    if os.path.exists('../../../PycharmProjects/testGoogleDrive/token.pickle'):
        with open('../../../PycharmProjects/testGoogleDrive/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Если нет доступных (действительных) учетных данных, дайте пользователю войти в систему.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраните учетные данные для следующего запуска
        with open('../../../PycharmProjects/testGoogleDrive/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def get_files(parents_id):
    service = get_service()

    results = service.files().list(pageSize=10,
                                   fields="nextPageToken, files(id, name, mimeType)").execute()
    nextPageToken = results.get('nextPageToken')
    while nextPageToken:
        nextPage = service.files().list(pageSize=10,
                                        parents=parents_id,
                                        fields="nextPageToken, files(id, name, mimeType, parents)",
                                        pageToken=nextPageToken).execute()
        nextPageToken = nextPage.get('nextPageToken')
        results['files'] = results['files'] + nextPage['files']
    return results.get('files')

def create_new_folder(parent_folder_id, name):
    service = get_service()

    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    r = service.files().create(body=file_metadata,
                               fields='id').execute()
    return r['id']

def upload_file(parent_folder_id, path, filename):
    service = get_service()

    folder_id = parent_folder_id
    name = filename
    file_path = os.path.join(path, name)
    file_metadata = {
        'name': name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return r['id']

def delete_file(fileid):
    service = get_service()

    service.files().delete(fileId=fileid).execute()
