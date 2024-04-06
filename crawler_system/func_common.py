import logging
import os
from datetime import datetime
import configparser

def setup_logging(log_retention_days=10):
    # log ディレクトリの相対パスを取得
    log_dir = os.path.join('..', 'log')

    # log ディレクトリが存在しない場合は作成
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 現在の日付と時刻を取得
    current_time = datetime.now()

    # ファイル名に使用する日付と時刻の文字列を作成
    formatted_time = current_time.strftime("%Y%m%d_%H%M%S")

    # ファイル名を作成 (log ディレクトリ内に保存)
    filename = os.path.join(log_dir, f'log_{formatted_time}.log')

    # ログのフォーマットを設定
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')

    # ファイルハンドラを設定 (INFOレベル)
    file_handler_info = logging.FileHandler(os.path.join(log_dir, f'log_info_{formatted_time}.log'))
    file_handler_info.setFormatter(formatter)
    file_handler_info.setLevel(logging.INFO)

    # コンソールハンドラを設定
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # ロガーにハンドラを追加
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # INFOレベルを設定して、DEBUGのメッセージをキャプチャしない
    logger.addHandler(file_handler_info)
    logger.addHandler(console_handler)

    # 古いログファイルを削除
    delete_old_logs(log_dir, log_retention_days)

def delete_old_logs(log_dir, log_retention_days):
    """
    古いログファイルを削除する。

    Args:
        log_dir (str): ログディレクトリのパス
        log_retention_days (int): ログを保持する日数
    """
    current_time = datetime.now()
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        # ファイルの最終更新時刻を取得
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        # ファイルの最終更新時刻が指定した日数を超えている場合、削除
        if (current_time - file_time).days > log_retention_days:
            os.remove(file_path)
            print(f"Deleted old log file: {file_path}")

def read_config_file(config_file_path):
    """
    Configファイルから設定を読み込む関数

    Args:
        config_file_path (str): Configファイルへのパス。

    Returns:
        dict: Configファイルから読み取った設定値を格納した辞書。
    """
    # configparserのインスタンスを作成
    config = configparser.ConfigParser()

    # 設定ファイルが存在するか確認
    if not os.path.exists(config_file_path):
        error_message = f"Error: Config file not found at {config_file_path}"
        print(error_message)
        logging.error(error_message)
        return None

    # 設定ファイルを読み込む
    config.read(config_file_path, encoding='utf-8')

    # 各セクションの設定を取得し、辞書に格納
    config_values = {}
    for section in config.sections():
        config_values[section] = {}
        for key, val in config.items(section):
            config_values[section][key] = val

    # logging.info(f"Config file {config_file_path} read successfully.")
    return config_values

def get_absolute_path(relative_path):
    """
    相対パスから絶対パスを生成する。

    引数:
        relative_path (str): 相対パス。

    戻り値:
        str: 絶対パス
    """
    # カレントディレクトリを取得
    current_dir = os.getcwd()

    # 絶対パスの生成
    absolute_path = os.path.abspath(os.path.join(current_dir, relative_path))

    return absolute_path