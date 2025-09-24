from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging
import pytesseract
from PIL import Image
import random
import string
import os

# 設定 Tesseract 路徑（Windows 使用者需調整）
pytesseract.pytesseract.tesseract_cmd = r"D:\Cent Brower\tesseract\tesseract.exe"  # 替換為您的 Tesseract 路徑

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

def capture_captcha_image():
    """擷取驗證碼圖片並保存"""
    try:
        captcha_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "CHK_pic"))  # 假設驗證碼圖片 ID
        )
        captcha_img.screenshot("captcha.png")
        logging.info("已擷取驗證碼圖片")
        return "captcha.png"
    except Exception as e:
        logging.error(f"擷取驗證碼圖片失敗: {str(e)}")
        return None

def preprocess_image(image_path):
    """簡單圖片預處理以提升 OCR 準確率"""
    try: 
        img = Image.open(image_path).convert("L")  # 轉為灰階
        img = img.resize((int(img.width * 2), int(img.height * 2)), Image.LANCZOS)  # 放大圖片
        img.save(image_path)
        logging.info("已完成圖片預處理")
    except Exception as e:
        logging.error(f"圖片預處理失敗: {str(e)}")

def recognize_captcha(image_path):
    """使用 Tesseract 識別驗證碼"""
    try:
        preprocess_image(image_path)
        text = pytesseract.image_to_string(Image.open(image_path), config="--psm 8").strip()
        # 清理文字，確保只保留大寫字母和數字
        cleaned_text = "".join(c for c in text.upper() if c in string.ascii_uppercase + string.digits)
        if len(cleaned_text) == 4:
            logging.info(f"識別到驗證碼: {cleaned_text}")
            return cleaned_text
        else:
            logging.warning(f"識別到的驗證碼長度不正確: {cleaned_text}")
            return None
    except Exception as e:
        logging.error(f"驗證碼識別失敗: {str(e)}")
        return None

def generate_random_captcha():
    """生成隨機4碼驗證碼（大寫字母或數字）"""
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for _ in range(4))

def verify_captcha():
    """自動輸入驗證碼並比對"""
    max_attempts = 10  # 最大嘗試次數
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        logging.info(f"驗證碼嘗試次數: {attempt}/{max_attempts}")

        # 擷取驗證碼圖片
        captcha_image_path = capture_captcha_image()
        if not captcha_image_path:
            logging.error("無法擷取驗證碼圖片，跳出手動輸入")
            return False

        # 嘗試 OCR 識別
        captcha_code = recognize_captcha(captcha_image_path)
        if not captcha_code:
            captcha_code = generate_random_captcha()
            logging.info(f"OCR 識別失敗，使用隨機驗證碼: {captcha_code}")

        # 輸入驗證碼
        try:
            captcha_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "CHK"))
            )
            captcha_input.clear()
            captcha_input.send_keys(captcha_code)
            logging.info(f"已輸入驗證碼: {captcha_code}")

            # 點擊加入購物車
            add_to_cart = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="addcart"]/button'))
            )
            add_to_cart.click()

            # 檢查是否成功（假設成功後跳轉到購物車頁面或無錯誤提示）
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[11]/div/button'))
                )
                logging.info("驗證碼正確，已進入購物車")
                return True
            except TimeoutException:
                # 檢查是否有錯誤提示
                try:
                    error_msg = driver.find_element(By.XPATH, "//*[contains(text(), '驗證碼錯誤')]")
                    logging.info("驗證碼錯誤，準備重試")
                except NoSuchElementException:
                    logging.info("無錯誤提示，但未進入購物車，準備重試")
        except Exception as e:
            logging.error(f"驗證碼輸入或提交失敗: {str(e)}")

    logging.error("超過最大嘗試次數，驗證碼驗證失敗")
    return False

try:
    # 步驟 1：開啟寬宏售票活動列表頁面
    driver.get("https://kham.com.tw/application/utk01/UTK0101_03.aspx")
    logging.info("已開啟寬宏售票網站")

    # 步驟 2：關閉可能的廣告彈窗
    close_ad_popup()

    # 步驟 3：點擊活動連結
    event_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="show-area"]/div[2]/div/a[5]/img'))
    )
    event_link.click()
    logging.info("已進入活動頁面")

    # 步驟 4：處理實名制提示窗口
    try:
        ok_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/div/button'))
        )
        ok_button.click()
        logging.info("已點擊實名制提示 OK 按鈕")
    except (NoSuchElementException, TimeoutException):
        logging.info("無實名制提示窗口")

    # 步驟 5：點擊「我要選票」或「立即選票」
    select_ticket_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="GO_BUY"]'))
    )
    select_ticket_button.click()
    logging.info("已點擊我要選票按鈕")

    # 步驟 6：點擊「立即訂購」
    order_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/table/tbody/tr[2]/td[4]/a/button'))
    )
    order_button.click()
    logging.info("已點擊立即訂購")

    # 步驟 7：選擇票區
    ticket_area = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="P0X1QMYD"]/td[2]'))
    )
    ticket_area.click()
    logging.info("已選擇票價區域")

    # 步驟 8：選擇票別
    ticket_type = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[3]/div[1]/div[1]/div[2]/button[1]'))  # 假設票別下拉選單 ID
    )
    ticket_type.send_keys("全票")  # 假設選擇「全票」，需調整為實際票別
    logging.info("已選擇票別")

    # 步驟 9：選定座位並輸入驗證碼
    seat = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="TBL"]/tbody/tr[10]/td[9]'))
    )
    seat.click()
    logging.info("已選擇座位")

    # 自動驗證碼處理
    if verify_captcha():
        logging.info("驗證碼驗證成功")
    else:
        logging.error("驗證碼驗證失敗，需手動介入")

    # 等待確認頁面
    time.sleep(5)

except Exception as e:
    logging.error(f"發生錯誤: {str(e)}")

finally:
    driver.quit()
    logging.info("程式結束")
    # 清理臨時圖片
    if os.path.exists("captcha.png"):
        os.remove("captcha.png")