# coding: utf-8
import time
import logging
import sys
import base64
import os
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# ローカルモジュールのインポート
sys.path.append('../scripts')
import func_line
import func_Gdrive


# ヘルパー関数
def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def createDirectory(dir_path):
    os.mkdir(dir_path)
def removeDirectory(dir_path):
    shutil.rmtree(dir_path)
def isExistsDirectory(dir_path):
    return os.path.isdir(dir_path)
def save_screenshot(driver, file_path, is_full_size=False):
    # スクリーンショット設定
    screenshot_config = {
        # Trueの場合スクロールで隠れている箇所も含める、Falseの場合表示されている箇所のみ
        "captureBeyondViewport": is_full_size,
    }
    # スクリーンショット取得
    base64_image = driver.execute_cdp_cmd("Page.captureScreenshot", screenshot_config)

    # ファイル書き出し
    with open(file_path, "wb") as fh:
        fh.write(base64.urlsafe_b64decode(base64_image["data"]))

    return file_path

# ========================================
# ログイン
# ========================================
def perform_login(driver, login_id, password):
    """
    Selenium WebDriverを使用してWebページにログインします。

    :param driver: 使用するSelenium WebDriverインスタンス
    :param login_id: ログインID
    :param password: ログインパスワード
    :return: ログインが成功した場合はTrue、失敗した場合はFalse
    """

    logging.info("ログインプロセスを開始します。")

    try:
        logging.info("ログインIDを入力します。")
        wait_for_element(driver, By.NAME, "login_id").send_keys(login_id)
        time.sleep(1)

        logging.info("パスワードを入力します。")
        wait_for_element(driver, By.NAME, "password").send_keys(password)
        time.sleep(1)

        # 「ログイン」ボタンをクリック
        logging.info("「ログイン」ボタンをクリックします。")
        wait_for_element(driver, By.CLASS_NAME, "button").send_keys(Keys.RETURN)

        return True

    except Exception as e:
        # エラーメッセージをログに出力
        logging.error(f"ログインプロセス中にエラーが発生しました: {str(e)}")
        return False  # エラーが発生した場合はFalseを返す


def get_shop_name(driver):
    try:
        # ショップのロゴがロードされるまで待ちます
        wait_for_element(driver, By.ID, 'logo')

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        shop_name = soup.find('div', {'id': 'logo'}).find('h1').get_text(strip=True)

        return shop_name
    except Exception as e:
        logging.error(f"ショップ名の取得に失敗しました: {e}")
        return None



# ========================================
# ポイント取得
# ========================================
def extract_shop_data(html_source):
    """
    指定されたHTMLソースから店舗名とURLを抽出します。

    Parameters
    ----------
    html_source : str
        抽出対象のHTMLソース

    Returns
    -------
    list[dict[str, str]]
        'shop_name' と 'url' キーを持つ辞書のリスト
    """
    # BeautifulSoup オブジェクト作成
    soup = BeautifulSoup(html_source, "html.parser")

    # 店舗リストを含むテーブルを検索
    table = soup.find("table", {"id": "shop-list-table"})
    if table is None:
        logging.error("テーブルが見つかりません。HTMLソースを確認してください。")
        return []

    # テーブル内のすべての行を抽出
    rows = table.find_all("tr", {"class": "shop-list-table-row"})

    # 各行から店舗名とURLを抽出
    result = []
    for row in rows:
        td = row.find("td")
        if td is None:
            logging.error("店舗名が見つかりません。HTMLソースを確認してください。")
            continue

        a_tag = row.find("a", {"class": "shoplogin"})
        if a_tag is None:
            logging.error("URLが見つかりません。HTMLソースを確認してください。")
            continue

        # 店舗名は最初のtd要素のテキスト
        shop_name = td.text

        # URLはaタグのhref属性
        url = a_tag.get('href')
        if url is None:
            logging.error("URLが見つかりません。HTMLソースを確認してください。")
            continue

        result.append({'shop_name': shop_name, 'url': url})

    return result




def get_month_start_and_end_based_on_date(input_date):
    """
    入力された日付を基に、その月の最初の日と最後の日を取得します。

    Parameters:
    input_date (datetime): 入力日付。

    Returns:
    tuple: 前月の最初の日と最後の日を '%Y-%m-%d' 形式の文字列として返します。

    Examples:
    >>> get_month_start_and_end_based_on_date(datetime(2023, 6, 1))
    ('2023-06-01', '2023-06-30')
    """
    # その月の最初の日と最後の日を取得
    first_day_of_month = input_date.replace(day=1)
    last_day_of_month = (first_day_of_month + relativedelta(months=1)) - timedelta(days=1)

    return first_day_of_month.strftime('%Y-%m-%d'), last_day_of_month.strftime('%Y-%m-%d')

def get_close_time_info(shop_name, html_source, check_date):
    """
    指定された日付に対応するレジ締め情報をHTMLコンテンツから取得します。

    Parameters:
    shop_name (str): 店舗名
    html_source (str): 解析対象のHTMLコンテンツ。
    check_date (str): レジ締め情報を取得したい日付。形式は '%Y-%m-%d' です。

    Returns:
    list: 店舗名、レジ締め日（形式：'%Y-%m-%d'）、レジ締め対象の開始時間、終了時間、関連URLの情報を含む辞書のリスト。
          レジ締め情報が見つからない場合、空のリストが返ります。

    Examples:
    >>> get_point_table('店舗A', '<html>...</html>', '2023-07-01')
    [{'shop_name': '店舗A', 'close_date': '2023-07-01', 'start_time': '09:00', 'end_time': '18:00', 'related_id': '888479'}]
    """
    # HTMLを解析します。
    soup = BeautifulSoup(html_source, "html.parser")

    # 指定したIDのdiv要素を探します。
    div_element = soup.find("div", {"id": "reserveInfo"})

    # div要素が存在しない場合、空のリストを返します。
    if div_element is None:
        return []

    # 表から各行を抽出します。
    rows = div_element.find("tbody").find_all("tr")
    
    check_date = check_date.strftime('%Y-%m-%d')

    result = []
    
    # 各行について処理します。
    for row in rows:
        cols = row.find_all("td")
        # "td" タグがない行をスキップします。
        if not cols:
            continue

        # レジ締め日と指定された日付が一致する場合に、その行のレジ締め対象日時と関連URLを取得します。
        close_date = cols[0].text.strip()
        if close_date == check_date:
            close_time_range = cols[1].text.split('～')
            start_time = close_time_range[0].strip()
            end_time = close_time_range[1].strip()
            related_id = row.find("a")["href"].split('=')[-1]  # この行が関連URLを持つという前提
            result.append({
                '店舗名': shop_name,
                'レジ締め日': close_date,
                'レジ締め開始日時': start_time,
                'レジ締め終了日時': end_time,
                'レジ締めID': related_id
            })

    return result

def get_close_time_info_for_shop(shop, driver, target_date):
    """
    指定された店舗にログインして、レジ締め情報を取得します。

    Parameters:
    shop (dict): ショップの情報を含む辞書。キーは'shop_name'と'url'。
    driver (webdriver object): ウェブサイトにアクセスするためのwebdriverオブジェクト。

    Returns:
    list: 指定店舗のレジ締め情報を含む辞書のリスト。

    Example:
    >>> get_close_time_info_for_shop({'shop_name':'Shop1', 'url':'http://shop1.com'}, driver)
    [{'shop_name': 'Shop1', 'close_date': '2023-07-01', 'start_time': '09:00', 'end_time': '18:00', 'related_id': '888479'}]
    """
    # 店舗にログイン
    logging.info(f'{shop["shop_name"]}にログインします。')
    driver.get(shop['url'])
    shop_name = get_shop_name(driver)
    logging.info(f'{shop_name}にログインしました。')


    # レジ締め一覧に移動
    # today = datetime.now()
    # yesterday = today - timedelta(days=1)
    start_date, end_date = get_month_start_and_end_based_on_date(target_date)
    url = f'https://b-merit.jp/manage/account/salesclose/?action=list&start_date={start_date}&end_date={end_date}'
    logging.info(f"レジ締め一覧に移動します：{url}")
    driver.get(url)

    # レジ締め日一覧取得
    html_source = driver.page_source
    logging.info(f'{shop_name}の売上データを取得します。')
    close_time_info = get_close_time_info(shop_name, html_source, target_date)

    return close_time_info

def extract_point_table_data(html_source):
    """
    ポイント利用情報データを抽出します。

    Parameters:
    html_source (str): 解析対象のHTMLコンテンツ。

    Returns:
    dict: 表の各行のth要素のテキストをキーとし、td要素のテキストを値とする辞書。

    """
    # HTMLを解析します。
    soup = BeautifulSoup(html_source, "html.parser")

    # 指定されたdiv要素から表を抽出します。
    table = soup.find("div", {"class": "register float", "style": "width:30%;"}).find("table", {"class": "manageTable formTable"})

    # 表から各行を抽出します。
    rows = table.find("tbody").find_all("tr")

    data = {}
    # 各行について処理します。
    for row in rows:
        th_text = row.find("th").text.strip()
        td_text = row.find("td").text.strip()
        data[th_text] = td_text

    return data

def get_point_data(info, driver):
    """
    指定されたレジ締めIDに対応するページに移動し、ポイント利用情報を取得します。

    Parameters:
    info (dict): レジ締め情報を含む辞書。キーは 'レジ締めID'。
    driver (webdriver object): ウェブサイトにアクセスするためのwebdriverオブジェクト。

    Returns:
    dict: レジ締め情報とポイント利用情報を結合した辞書。

    Example:
    >>> get_point_data({'レジ締めID':'888479'}, driver)
    {'レジ締めID': '888479', 'point_date': '2023-07-01', 'point_amount': '100'}
    """
    url = f"https://b-merit.jp/manage/account/salesclose/?action=detail&id={info['レジ締めID']}"
    logging.info(f"対象日のレジ締め対象ページに移動します：{url}")
    driver.get(url)
    time.sleep(1)

    logging.info("ポイント利用情報を取得")
    html_source = driver.page_source
    point_data = extract_point_table_data(html_source)
    logging.info(point_data)

    combined_data = {**info, **point_data}

    return combined_data

def process_shop_data(shop_data, driver, line_access_token, target_date):
    """
    店舗データのリストを処理して、各店舗のレジ締め情報とポイント利用情報を取得します。

    Parameters:
    shop_data (list): 店舗データのリスト。各要素は店舗情報を含む辞書。
    driver (webdriver object): ウェブサイトにアクセスするためのwebdriverオブジェクト。

    Returns:
    None. Function updates the passed 'point_tables' list.

    Example:
    >>> point_tables = []
    >>> process_shop_data([{'shop_name':'Shop1', 'url':'http://shop1.com'}], driver, point_tables)
    >>> print(point_tables)
    [{'shop_name': 'Shop1', 'close_date': '2023-07-01', 'start_time': '09:00', 'end_time': '18:00', 'related_id': '888479', 'point_date': '2023-07-01', 'point_amount': '100'}]
    """
    point_tables = []
    df = pd.DataFrame()

    for shop in shop_data:
        logging.info('------------------------------')
        try:
            close_time_info = get_close_time_info_for_shop(shop, driver, target_date)
            if not close_time_info:
                # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
                # LINE通知する
                message = f'{shop["shop_name"]}にレジ締め情報なし'
                logging.warning(message)
                func_line.notify_line(line_access_token, message)

                # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
                continue
            for info in close_time_info:
                logging.info(f"レジ締め日: {info['レジ締め日']}, レジ締め対象時間: {info['レジ締め開始日時']}～{info['レジ締め終了日時']}, 関連ID: {info['レジ締めID']}")

                combined_data = get_point_data(info, driver)
                point_tables.append(combined_data)

                # ポイント利用情報用の取得
                df = pd.DataFrame(point_tables)
                df = df.fillna(0).astype(str)
                df = df.applymap(lambda x: x.replace('円', '').replace(',', '').replace('pt', '').strip())

        except Exception as e:
            logging.error(f'Error processing shop {shop}: {str(e)}')

    return df


# ==============================
# 売上データを抽出
# ==============================



def parse_html_to_dataframe(html, shop_name):
    """
    HTMLから売上データを抽出し、データフレームを作成する。

    Parameters:
    html : str
        BeautifulSoupで解析するHTML。

    shop_name : str
        取得する店舗の名前。

    Returns:
    df : DataFrame
        抽出した売上データのデータフレーム。データが存在しない場合は空のデータフレームを返す。
    """

    # BeautifulSoup オブジェクトを作成
    soup = BeautifulSoup(html, 'html.parser')

    # テーブルを見つける
    table = soup.find('table', {'id': 'account_data'})

    # テーブルがなければ、空のデータフレームを返す
    if table is None:
        return pd.DataFrame()

    # テーブルのすべての行を抽出
    rows = table.find_all('tr')

    # データを保存するための空のリストを作成
    data = []

    # 各行をループ
    for row in rows[2:]:  # ヘッダ行をスキップ
        ths = row.find_all('th')
        # th要素の数をチェックして、合計行をスキップ
        if len(ths) < 2:
            continue

        cols = row.find_all('td')

        # 各列をループしてテキストを抽出、なければnull値を追加
        cols_text = []
        for col in cols:
            text = col.get_text(strip=True) if col else np.nan
            cols_text.append(text)

        # 日付と曜日を取得、なければnull値を追加
        date = ths[0].get_text(strip=True) if ths else np.nan
        weekday = ths[1].get_text(strip=True) if ths else np.nan

        # 日付と曜日を列のテキストに追加
        cols_text.insert(0, date)
        cols_text.insert(1, weekday)

        data.append(cols_text)

    # ヘッダーを指定
    headers = ['日付', '曜日', '純売上', '技術', '商品', 'その他', '総売上', '割引', '客単価', '総客数', '新規', '再来', '指名売上', '技術', '商品', 'その他', '割引', '指名客単価', '指名数']

    # データフレームを作成
    df = pd.DataFrame(data, columns=headers)

    # 全ての列で、「円」とカンマを削除
    df = df.astype(str)
    df = df.applymap(lambda x: x.replace('円', '').replace(',', '').strip())
    # 日付列をYYYY-MM-DD形式に変換
    df['日付'] = pd.to_datetime(df['日付'], format='%Y年%m月%d日').dt.strftime('%Y-%m-%d')

    # 店舗名列を追加
    df.insert(0, '店舗名', shop_name)

    return df

def collect_all_shop_data(shop_data, driver, target_date, service, screenshot_folder_id):
    """
    各店舗の売上データを収集し、結合したデータフレームを返す。

    Parameters:
    shop_data : list
        各店舗の情報が辞書形式で格納されたリスト。
        辞書には各店舗の名前とURLが含まれている必要がある。

    driver : WebDriver object
        Selenium WebDriverオブジェクト。

    Returns:
    df_all_shops : DataFrame
        各店舗の売上データを結合したデータフレーム。
    """

    # 空のデータフレームを準備
    df_all_shops = pd.DataFrame()

    # スクリーンショットを一時的に保存するディレクトリを作成
    screenshot_dir_path = '../screenshot'
    if not (isExistsDirectory(screenshot_dir_path)):
        createDirectory(screenshot_dir_path)
    # スクリーンショットのファイル名に使用
    today = datetime.now()
    target_year = f'{today.strftime("%Y")}年'
    target_month = f'{today.strftime("%-m")}月'
    datetime_string = f'{today.strftime("%Y%m%d")}_{today.strftime("%H%M")}'

    for shop in shop_data:
        logging.info('------------------------------')
        try:
            # 店舗にログイン
            logging.info(f'{shop["shop_name"]}にログインします。')
            driver.get(shop['url'])
            shop_name = get_shop_name(driver)
            logging.info(f'{shop_name}にログインしました。')

            # 全画面スクリーンショット取得
            file_path = f'../screenshot/{shop_name}_{datetime_string}.png'
            save_screenshot(driver, file_path, is_full_size=True)
            # スクリーンショットをアップロード
            shop_folder_id = func_Gdrive.getFolderList(service, shop_name, screenshot_folder_id)
            year_folder_id = func_Gdrive.getFolderList(service, target_year, shop_folder_id)
            month_folder_id = func_Gdrive.getFolderList(service, target_month, year_folder_id)
            func_Gdrive.upload_file(service, file_path, month_folder_id)

            start_date, end_date = get_month_start_and_end_based_on_date(target_date)
            url = f'https://b-merit.jp/manage/analysis/account?periodType=0&startDay={start_date}&endDay={end_date}'
            logging.info(f"売上分析ページに移動します。{url}")
            driver.get(url)
            html_source = driver.page_source
            logging.info(f'{shop_name}の売上データを取得します。')
            df = parse_html_to_dataframe(html_source, shop_name)
        except Exception as e:
            logging.error(f'売上データの取得中にエラーが発生しました: {e}')
            continue

        # dfが空ではない場合、結合する
        if not df.empty:
            df_all_shops = pd.concat([df_all_shops, df], ignore_index=True)

    # スクリーンショットを一時的に保存していたディレクトリを削除
    removeDirectory(screenshot_dir_path)

    return df_all_shops
