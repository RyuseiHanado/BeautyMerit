# 標準ライブラリのインポート
import sys
import logging

# ローカルモジュールのインポート
sys.path.append('../scripts')
import func_common
import func_Gdrive

# コード
func_common.setup_logging()

config_file_path = '../config/config.ini'  # config.iniファイルのパスを適切に設定してください
config_values = func_common.read_config_file(config_file_path)

# アップロード先フォルダID取得
gdrive_config = config_values['Gdrive']
screenshot_folder_id = gdrive_config['screenshot_folder_id']
service = func_Gdrive.authenticate_gdrive()


def main():
    print('statt')

#     アップロード先フォルダID取得
    gdrive_config = config_values['Gdrive']
    upload_folder_id = gdrive_config['upload_folder_id']
    service = func_Gdrive.authenticate_gdrive()

    csv_path = '../downloads/sample.txt'

    folder_name = 'サンプルフォルダ'
    folder_id = func_Gdrive.getFolderList(service, screenshot_folder_id, folder_name)
    func_Gdrive.upload_file(service, csv_path, folder_id)

if __name__ == "__main__":
    try:
        main()
        logging.info(f"処理が完了しました。")

    except Exception as e:
        logging.info(f"エラーが発生しました: {e}")
    # finally:
        # input("何かキーを押して終了してください...")