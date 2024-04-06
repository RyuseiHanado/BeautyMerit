# https://www.marketechlabo.com/python-google-auth/

from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import logging
import os

service_account_file = '../config/client_secrets.json' # サービスアカウントのJSONキーファイルのパス

API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive'] # 共有ドライブへのアクセスにはこれを使用

def authenticate_gdrive():
    try:
        creds = Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
        logging.info("Google Driveへの認証が成功しました。")
    except Exception as e:
        logging.error(f"Google Driveへの認証に失敗しました。エラー: {str(e)}")
        raise

    return build(API_NAME, API_VERSION, credentials=creds)

def upload_file(service, filepath, folder_id):
    filename = os.path.basename(filepath)
    media = MediaFileUpload(filepath)
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        supportsAllDrives=True # これを追加
    ).execute()

    try:
        logging.info(f"ファイルが正常にアップロードされました！")
        logging.info(f"  URL(ファイル): https://docs.google.com/document/d/{str(file['id'])}")
        logging.info(f"  URL(フォルダ): https://drive.google.com/drive/u/1/folders/{folder_id}")
    except Exception as e:
        logging.error(f"ファイルのアップロードに失敗しました。エラー: {str(e)}")
        return None
    
def getFolderList(service):
    directory_id = '1CRoGsJwiYKsFo4RtbLJP7ZDe2Ymy-NPd'
    results = service.files().list(
        q=f"'{directory_id}' in parents and "
              "trashed = false",
        pageSize=100,
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
