# https://chat.openai.com/c/6853754a-af51-4003-8ed1-43d856899ea7

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging

def set_driver():
    """
    Seleniumを使用してChrome WebDriverを作成する。

    戻り値:
        WebDriver: Chrome WebDriver インスタンス
    """
    options = Options()
    options.headless = True
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

    prefs = {}
    prefs['download.prompt_for_download'] = False # ダウンロードあり
    prefs['download.directory_upgrade'] = True # ダウンロードあり
    options.add_experimental_option('prefs', prefs)

    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    service = Service(ChromeDriverManager().install())
    # service = Service(ChromeDriverManager("114.0.5735.16").install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(60)
    driver.set_window_size(1980,1080)

    return driver
