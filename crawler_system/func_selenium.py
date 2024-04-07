# https://chat.openai.com/c/6853754a-af51-4003-8ed1-43d856899ea7

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging

def set_driver():
    logging.info('set driver is invoked --------')
    """
    Seleniumを使用してChrome WebDriverを作成する。

    戻り値:
        WebDriver: Chrome WebDriver インスタンス
    """
    options = Options()
    options.headless = True
    logging.info('kikk 1 --------')
    # options.add_argument("--incognito")  # シークレットモードの設定を付与
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument('--disable-extensions')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # options.add_argument('--start-maximized')
    options.add_argument("window-size=1920x1080") 
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    # options.add_experimental_option("prefs", prefs)

    logging.info('kikk 2 --------')

    prefs = {}
    prefs['download.prompt_for_download'] = False # ダウンロードあり
    prefs['download.directory_upgrade'] = True # ダウンロードあり
    options.add_experimental_option('prefs', prefs)

    logging.info('kikk 3 --------')

    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    logging.info('kikk 4 --------')

    service = Service(ChromeDriverManager().install())
    logging.info('kikk 5 --------')
    # service = Service(ChromeDriverManager("114.0.5735.16").install())
    logging.info('kikk 6 --------')
    driver = webdriver.Chrome(service=service, options=options)
    logging.info('kikk 7 --------')
    driver.implicitly_wait(10)
    logging.info('kikk 8 --------')
    driver.set_page_load_timeout(60)
    logging.info('kikk 9 --------')

    return driver
