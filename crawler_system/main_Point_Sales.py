#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ログイン処理
# https://chat.openai.com/c/f224d159-3a13-46d2-9470-0f1a0f164ab4

# selenium
# https://chat.openai.com/c/406ac40b-addf-4e35-b04d-49c38d8aa6c3


# In[2]:


# coding: utf-8

# 標準ライブラリのインポート
import sys
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

# ローカルモジュールのインポート
sys.path.append('../scripts')
import func_common
import func_selenium
import func_BM
import func_line
import func_Gdrive

# 仮想ディスプレイで使用
import pyvirtualdisplay


# In[3]:


def main():
    # ========================================
    # 初期設定
    # ========================================

    # コード
    func_common.setup_logging()

    # 仮想ディスプレイ環境を構築
    display = pyvirtualdisplay.Display(visible=0, size=(1980, 1080))
    display.start()

    config_file_path = '../config/config.ini'  # config.iniファイルのパスを適切に設定してください
    config_values = func_common.read_config_file(config_file_path)
    # account_keys = ['Beauty_Merit_Account1', 'Beauty_Merit_Account2', 'Beauty_Merit_Account3']
    account_keys = ['Beauty_Merit_Account1']
    downloads_path = '../downloads'
    base_url = "https://b-merit.jp/groupmanage/login/?redirect=1"

    # LINE通知用トークン情報取得
    line_config = config_values['LINE']
    line_access_token = line_config['access_token']

    # アップロード先フォルダID取得
    gdrive_config = config_values['Gdrive']
    upload_folder_id = gdrive_config['upload_folder_id']
    screenshot_folder_id = gdrive_config['screenshot_folder_id']
    service = func_Gdrive.authenticate_gdrive()


    # ========================================
    # メイン処理
    # ========================================
    message = 'ポイント、売上データの抽出処理を開始します'
    response= func_line.notify_line(line_access_token, message)

    for account_key in account_keys:
        logging.info('================================================================')
        # ログイン処理
        bm_config = config_values[account_key]
        login_id = bm_config['login_id']
        password = bm_config['password']

        driver = func_selenium.set_driver()
        driver.get(base_url)
        logging.info(f"アカウント名：{login_id} でログインします")
        func_BM.perform_login(driver, login_id, password)

        # 店舗名とURLを抽出する
        html_source = driver.page_source
        shop_data = func_BM.extract_shop_data(html_source)

        # 取得したデータが空かどうかチェック
        if len(shop_data) == 0:
            logging.error("店舗名とURLデータの取得に失敗しました。")
            sys.exit(1)
        else:
            logging.info(f"店舗名とURLデータの取得しました。取得件数: {len(shop_data)}")

        # 結果の表示
        for shop in shop_data:
            logging.info(f"{shop['shop_name']}, {shop['url']}")

        # メイン処理
        today = datetime.now()
        target_date = today - relativedelta(days=1) # 前日
        logging.info(f"対象日：{target_date}")
        # ファイル出力用変数
        today = datetime.today().strftime('%Y%m%d')
        login_id = login_id.split('@')[0]
        # ポイント利用情報用の取得、エクスポート
        logging.info('==================================================')
        logging.info('ポイント利用情報用の取得、エクスポート、ファイルアップロード')
        logging.info('==================================================')
        # ------- df_all_shops_point = func_BM.process_shop_data(shop_data, driver, line_access_token, target_date)
        df_all_shops_point = func_BM.process_shop_data([shop_data[0]], driver, line_access_token, target_date)
        if not df_all_shops_point.empty:  # データフレームが空でない場合にcsv出力
            # point_csv_filename = f'{downloads_path}/point_tables_{login_id}_{today}.csv'
            point_csv_filename = f'{downloads_path}/point_tables_{login_id}_{target_date.strftime("%Y%m%d")}.csv'  # ここ追加した。削除必要
            df_all_shops_point.to_csv(point_csv_filename, index=False, encoding='UTF-8')
            logging.info(f'ポイントcsv出力：{point_csv_filename}')
            # GDriveへアップロード
            if not (func_Gdrive.isExistsFile(service, point_csv_filename, upload_folder_id)):
                logging.info(f'GDriveへアップロード')
                func_Gdrive.upload_file(service, point_csv_filename, upload_folder_id)
                logging.info('ポイント利用情報用の取得、エクスポート、ファイルアップロードが完了しました。')
            else:
                logging.info('GDriveに同名のファイルが存在するためアップロードをキャンセルしました')

        else:
            logging.warning('ポイント利用情報用の取得するデータがありませんでした。')

        # 売上データ取得、エクスポート
        logging.info('==================================================')
        logging.info('売上データ取得、エクスポート、ファイルアップロード')
        logging.info('==================================================')
        # ------- df_all_shops_sales = func_BM.collect_all_shop_data(shop_data, driver, target_date, service, screenshot_folder_id)
        df_all_shops_sales = func_BM.collect_all_shop_data([shop_data[0]], driver, target_date, service, screenshot_folder_id)
        if not df_all_shops_sales.empty:  # データフレームが空でない場合にcsv出力
            # csv出力
            salse_csv_filename = f'{downloads_path}/sales_tables_{login_id}_{target_date.strftime("%Y%m%d")}.csv'  # ファイル名をsales_tablesに変更
            df_all_shops_sales.to_csv(salse_csv_filename, index=False, encoding='UTF-8')
            logging.info(f'売上csv出力：{salse_csv_filename}')
            # GDriveへアップロード
            if not (func_Gdrive.isExistsFile(service, salse_csv_filename, upload_folder_id)):
                logging.info(f'GDriveへアップロード')
                func_Gdrive.upload_file(service, salse_csv_filename, upload_folder_id)
                logging.info('売上データ取得、エクスポート、ファイルアップロードが完了しました。')
            else:
                logging.info('GDriveに同名のファイルが存在するためアップロードをキャンセルしました')
        else:
            logging.warning('売上データの取得するデータがありませんでした。')

        # 各アカウントの処理が終わったら、ブラウザを閉じます。
        driver.quit()

    message = 'ポイント、売上データの抽出処理を終了しました。'
    response = func_line.notify_line(line_access_token, message)


# In[4]:


if __name__ == "__main__":
    try:
        main()
        logging.info(f"処理が完了しました。")

    except Exception as e:
        logging.info(f"エラーが発生しました: {e}")
    # finally:
        # input("何かキーを押して終了してください...")

