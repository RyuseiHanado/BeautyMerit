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

def upload_file(service, file_path, folder_id):
    filename = os.path.basename(file_path)
    media = MediaFileUpload(file_path)
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
    
def getFolderList(service, folder_name, root_folder_id):
    # root_folder_id で特定のフォルダ内を検索
    # mimeType=*** でフォルダのみを検索
    # folder_name に一致するフォルダを検索
    # ゴミ箱をは検索しない
    results = service.files().list(
        q=f"'{root_folder_id}' in parents and "
            "mimeType='application/vnd.google-apps.folder' and"
            f"name = '{folder_name}' and "
            "trashed = false",
        pageSize=10,
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])

    if not items:
        logging.info(f'{folder_name} フォルダが見つかりませんでした')
        return createFolder(service, folder_name, root_folder_id)
    else:
        print('フォルダ一覧:')
        for item in items:
            logging.info(u'{0} ({1})'.format(item['name'], item['id']))
        return items[0]['id']

def isExistsFile(service, file_path, root_folder_id):
    file_name = os.path.basename(file_path)
    logging.info(f'ファイル名: {file_name}')
    # root_folder_id で特定のフォルダ内を検索
    # file_name に一致するファイルを検索
    # ゴミ箱をは検索しない
    results = service.files().list(
        q=f"'{root_folder_id}' in parents and "
          f"name = '{file_name}' and "
          "trashed = false",
        pageSize=10,
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])
    return items

def createFolder(service, folder_name, root_folder_id):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [root_folder_id]
    }
    folder = service.files().create(body=file_metadata,
                                fields='id').execute()

    #fieldに指定したidをfileから取得できる
    logging.info(f'{folder_name} フォルダを作成')
    folder_id = folder.get('id')
    logging.info(f'Folder ID: %s' % folder.get('id'))
    return folder_id
