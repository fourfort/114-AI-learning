from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 設定 ChromeDriver 路徑
CHROMEDRIVER_PATH = r"D:\Cent Brower\chromedriver-win64\chromedriver.exe"

# 設定 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # 最大化視窗
# chrome_options.add_argument("--headless")  # 若不需顯示瀏覽器，取消註解此行

# 初始化 WebDriver
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

def close_ad_popup():
    """嘗試關閉廣告彈窗"""
    try:
        close_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="form1"]/div[4]/div/div[1]'))
        )
        close_button.click()
        logging.info("已關閉廣告彈窗")
    except (NoSuchElementException, TimeoutException):
        logging.info("無廣告彈窗或無法找到關閉按鈕")

try:
    # 步驟 1：開啟寬宏售票活動列表頁面
    driver.get("https://kham.com.tw/application/utk01/UTK0101_03.aspx")
    logging.info("已開啟寬宏售票網站")

    # 步驟 2：關閉可能的廣告彈窗
    close_ad_popup()

    # # 步驟 3：檢查是否需要登入
    # try:
    #     login_link = WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '會員登入')]"))
    #     )
    #     login_link.click()
    #     logging.info("進入登入頁面")

    #     # 輸入身份證號碼、密碼和驗證碼
    #     id_input = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "txtID"))  # 假設身份證輸入框 ID
    #     )
    #     id_input.send_keys("您的身份證號碼")  # 替換為實際身份證號碼

    #     password_input = driver.find_element(By.ID, "txtPassword")  # 假設密碼輸入框 ID
    #     password_input.send_keys("您的密碼")  # 替換為實際密碼

    #     captcha_input = driver.find_element(By.ID, "txtCaptcha")  # 假設驗證碼輸入框 ID
    #     captcha_code = input("請輸入4碼驗證碼（大寫字母或數字）：")  # 手動輸入驗證碼
    #     captcha_input.send_keys(captcha_code)

    #     submit_login = driver.find_element(By.ID, "btnLogin")  # 假設登入按鈕 ID
    #     submit_login.click()
    #     logging.info("已完成登入")

    #     # 再次關閉可能的廣告彈窗
    #     close_ad_popup()
    # except (NoSuchElementException, TimeoutException):
    #     logging.info("已登入或無需登入")

    # 步驟 4：點擊活動連結
    event_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="show-area"]/div[2]/div/a[5]/img'))
    )
    event_link.click()
    logging.info("已進入活動頁面")

    # 步驟 5：處理實名制提示窗口
    try:
        ok_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/div/button'))
        )
        ok_button.click()
        logging.info("已點擊實名制提示 OK 按鈕")
    except (NoSuchElementException, TimeoutException):
        logging.info("無實名制提示窗口")

    # 步驟 6：點擊「我要選票」或「立即選票」
    select_ticket_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="GO_BUY"]'))
    )
    select_ticket_button.click()
    logging.info("已點擊我要選票按鈕")

    # 步驟 7：點擊「立即訂購」
    order_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/table/tbody/tr[2]/td[4]/a/button'))  # 假設與原程式碼相同
    )
    order_button.click()
    logging.info("已點擊立即訂購")

    # 步驟 8：選擇票區
    ticket_area = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="P0X1QMYD"]/td[2]'))  # 調整為實際票價
    )
    ticket_area.click()
    logging.info("已選擇票價區域")

    # 步驟 9：選定座位並輸入驗證碼
    seat = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="TBL"]/tbody/tr[9]/td[9]'))  # 假設可用座位 Class
    )
    seat.click()
    logging.info("已選擇座位")

    captcha_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "CHK"))  # 假設驗證碼輸入框 ID
    )
    captcha_code = input("請輸入座位選擇頁面的4碼驗證碼（大寫字母或數字）：")  # 手動輸入驗證碼
    captcha_input.send_keys(captcha_code)

    add_to_cart = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="addcart"]/button'))  # 假設加入購物車按鈕 ID
    )
    add_to_cart.click()
    logging.info("已點擊加入購物車")

    # 等待確認頁面
    time.sleep(5)

except Exception as e:
    logging.error(f"發生錯誤: {str(e)}")

finally:
    driver.quit()
    logging.info("程式結束")