# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
from PIL import Image
import time
import logging
import pytesseract
import random
import string
import os

# 設定 Tesseract 路徑
pytesseract.pytesseract.tesseract_cmd = r"D:\Cent Brower\tesseract\tesseract.exe"

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 設定 ChromeDriver 路徑
CHROMEDRIVER_PATH = r"D:\Cent Brower\chromedriver-win64\chromedriver.exe"

# 設定 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # 最大化視窗
chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 硬體加速
chrome_options.add_argument("--no-sandbox")  # 禁用沙箱模式
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")  # 模擬真實瀏覽器
# chrome_options.add_argument("--headless")  # 若需無頭模式，取消註解

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
        time.sleep(random.uniform(0.5, 1.5))
    except (NoSuchElementException, TimeoutException):
        logging.info("無廣告彈窗或無法找到關閉按鈕")

def capture_captcha_image():
    """擷取驗證碼圖片並保存"""
    try:
        captcha_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="chk_pic"]'))
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

def handle_popup(is_success=False):
    """處理彈出窗口（alert 或 HTML 彈出窗口）"""
    try:
        # 嘗試處理 JavaScript alert
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_text = alert.text
        logging.info(f"檢測到 alert 窗口，內容: {alert_text}")
        alert.accept()
        logging.info("已關閉 alert 窗口")
        time.sleep(random.uniform(0.5, 1.5))
        return True
    except (TimeoutException, NoAlertPresentException):
        logging.info("無 JavaScript alert，嘗試處理 HTML 彈出窗口")

    try:
        # 處理 HTML 彈出窗口
        close_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[contains(@class, "close") or contains(text(), "關閉") or contains(@class, "modal-close") or contains(@aria-label, "close")]')
            )
        )
        close_button.click()
        logging.info(f"已關閉 HTML 彈出窗口（{'成功' if is_success else '失敗'}）")
        time.sleep(random.uniform(0.5, 1.5))
        return True
    except (NoSuchElementException, TimeoutException):
        logging.warning("未找到 HTML 彈出窗口關閉按鈕")
        return False

def refresh_captcha():
    """嘗試刷新驗證碼圖片"""
    try:
        refresh_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="chk_pic"]'))
        )
        refresh_button.click()
        logging.info("已刷新驗證碼圖片")
        time.sleep(random.uniform(0.5, 1.5))
    except (NoSuchElementException, TimeoutException):
        logging.info("未找到驗證碼刷新按鈕，繼續使用現有圖片")

def verify_captcha():
    """自動輸入驗證碼並比對，處理成功和失敗的彈出窗口"""
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        logging.info(f"驗證碼嘗試次數: {attempt}/{max_attempts}")

        # 刷新驗證碼圖片（若有刷新按鈕）
        refresh_captcha()

        # 擷取驗證碼圖片
        captcha_image_path = capture_captcha_image()
        if not captcha_image_path:
            logging.error("無法擷取驗證碼圖片，跳出手動輸入")
            return False

        # 識別驗證碼
        captcha_code = recognize_captcha(captcha_image_path)
        if not captcha_code:
            captcha_code = generate_random_captcha()
            logging.info(f"OCR 識別失敗，使用隨機驗證碼: {captcha_code}")

        try:
            # 輸入驗證碼
            captcha_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "CHK"))
            )
            captcha_input.clear()
            captcha_input.send_keys(captcha_code)
            logging.info(f"Entered captcha: {captcha_code}")
            time.sleep(random.uniform(0.5, 1.5))

            # 點擊加入購物車
            add_to_cart = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="addcart"]/button'))
            )
            add_to_cart.click()
            time.sleep(random.uniform(0.5, 1.5))

            # 檢查是否成功
            try:
                WebDriverWait(driver, 3).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '購物車')]")),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '成功')]"))
                    )
                )
                # 處理成功彈出窗口
                if handle_popup(is_success=True):
                    logging.info("驗證碼正確，已關閉成功窗口")
                else:
                    logging.warning("未檢測到成功窗口，但已進入購物車")
                return True
            except TimeoutException:
                # 檢查是否出現失敗窗口
                try:
                    WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '驗證碼錯誤')]"))
                    )
                    # 處理失敗彈出窗口
                    if handle_popup(is_success=False):
                        logging.info("驗證碼錯誤，已關閉失敗窗口，準備重試")
                    else:
                        logging.info("驗證碼錯誤，未檢測到失敗窗口，準備重試")
                except TimeoutException:
                    logging.info("無錯誤提示，準備重試")
        except Exception as e:
            logging.error(f"驗證碼輸入或提交失敗: {str(e)}")

    logging.error("超過最大嘗試次數，驗證碼驗證失敗")
    return False

def check_login_status():
    """檢查是否已登入"""
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), '登出') or contains(text(), '會員中心') or contains(@id, 'logout')]")
            )
        )
        logging.info("已檢測到登入狀態")
        return True
    except TimeoutException:
        logging.info("未檢測到登入狀態，需手動登入")
        return False

def check_login_error():
    """檢查登入頁面是否有錯誤提示"""
    try:
        error_msg = driver.find_element(By.XPATH, "//*[contains(text(), '驗證碼錯誤') or contains(text(), '帳號或密碼錯誤')]")
        logging.error(f"登入錯誤: {error_msg.text}")
        return True
    except NoSuchElementException:
        return False

try:
    # 步驟 1：開啟寬宏售票活動列表頁面
    driver.get("https://kham.com.tw/application/utk01/UTK0101_03.aspx")
    logging.info("已開啟寬宏售票網站")
    logging.info(f"當前 URL: {driver.current_url}")
    time.sleep(random.uniform(0.5, 1.5))

    # 步驟 2：關閉可能的廣告彈窗
    close_ad_popup()

    # 步驟 3：檢查是否已登入
    if not check_login_status():
        # 步驟 4：進入登入頁面並等待手動登入
        try:
            login_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="user"]/a/img')
                )
            )
            login_link.click()
            logging.info("已進入登入頁面")
            logging.info(f"當前 URL: {driver.current_url}")
            time.sleep(random.uniform(0.5, 1.5))

            # 提示手動輸入
            while True:
                print("請在瀏覽器中輸入身份證號碼、密碼和驗證碼，點擊「提交」按鈕後，在此按 Enter 繼續...")
                input()
                if not check_login_error():
                    break
                print("偵測到登入錯誤（例如驗證碼或帳密錯誤），請重新輸入並提交，然後按 Enter 繼續...")

            # 等待跳轉到系統畫面
            WebDriverWait(driver, 120).until(
                EC.any_of(
                    EC.url_contains("UTK0101_03.aspx"),
                    EC.url_contains("utk1306_.aspx"),
                )
            )
            logging.info("已跳轉到系統畫面")
            logging.info(f"當前 URL: {driver.current_url}")
        except TimeoutException as e:
            logging.error(f"登入後未回到系統畫面: {str(e)}")
            logging.error(f"當前 URL: {driver.current_url}")
            raise Exception("登入失敗，請檢查手動登入是否成功或更新等待條件")
        except NoSuchElementException as e:
            logging.error(f"無法找到登入連結: {str(e)}")
            logging.error(f"當前 URL: {driver.current_url}")
            raise Exception("登入連結選擇器錯誤，請檢查 XPath 或頁面結構")

    # 步驟 5：關閉可能的廣告彈窗
    close_ad_popup()

    # 步驟 6：確保位於活動列表頁面
    if not driver.current_url.endswith("UTK0101_03.aspx"):
        driver.get("https://kham.com.tw/application/utk01/UTK0101_03.aspx")
        logging.info("已重新導向至活動列表頁面")
        logging.info(f"當前 URL: {driver.current_url}")
        time.sleep(random.uniform(0.5, 1.5))
        close_ad_popup()

    # 步驟 7：點擊活動連結
    event_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="show-area"]/div[2]/div/a[5]/img'))
    )
    event_link.click()
    logging.info("已進入活動頁面")
    time.sleep(random.uniform(0.5, 1.5))

    # 步驟 8：處理實名制提示窗口
    try:
        ok_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/div/button'))
        )
        ok_button.click()
        logging.info("已點擊實名制提示 OK 按鈕")
        time.sleep(random.uniform(0.5, 1.5))
    except (NoSuchElementException, TimeoutException):
        logging.info("無實名制提示窗口")

    # 步驟 9：點擊「我要選票」或「立即選票」
    select_ticket_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="GO_BUY"]'))
    )
    select_ticket_button.click()
    logging.info("已點擊我要選票按鈕")
    time.sleep(random.uniform(0.5, 1.5))

    # 步驟 10：點擊「立即訂購」
    order_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/table/tbody/tr[2]/td[4]/a/button'))
    )
    order_button.click()
    logging.info("已點擊立即訂購")
    time.sleep(random.uniform(0.5, 1.5))

    # 步驟 11：選擇票區
    ticket_area = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="P0X1QMYD"]/td[2]'))
    )
    ticket_area.click()
    logging.info("已選擇票價區域")
    time.sleep(random.uniform(0.5, 1.5))

    # 步驟 12：選擇票別
    try:
        ticket_type = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[3]/div[1]/div[1]/div[2]/button[1]'))
        )
        # 使用 ActionChains 模擬懸停和點擊
        actions = ActionChains(driver)
        actions.move_to_element(ticket_type).pause(0.5).click().perform()
        logging.info("已點擊票別按鈕")
        time.sleep(random.uniform(0.5, 1.5))

        # 驗證票別是否選中
        WebDriverWait(driver, 5).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[3]/div[1]/div[1]/div[2]/button[1][contains(@class, "active") or contains(@class, "selected")]')),
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '票價')]")),
            )
        )
        logging.info("票別已成功選中")
    except TimeoutException as e:
        logging.error(f"票別選擇失敗，可能是按鈕未選中: {str(e)}")
        logging.error(f"當前 URL: {driver.current_url}")
        raise Exception("票別按鈕選擇失敗，請檢查選擇器或按鈕交互")

    # 步驟 13：選定座位並輸入驗證碼
    seat = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="TBL"]/tbody/tr[9]/td[9]'))
    )
    seat.click()
    logging.info("已選擇座位")
    time.sleep(random.uniform(0.5, 1.5))

    # 自動驗證碼處理
    if verify_captcha():
        logging.info("驗證碼驗證成功")
        # 等待確認頁面
        time.sleep(random.uniform(2, 3))
        logging.info("已完成搶票流程，網站保持開啟")
    else:
        logging.error("驗證碼驗證失敗，無法完成動作")
        # 即使失敗，保持網站開啟
        logging.info("網站保持開啟，需手動確認")

except Exception as e:
    logging.error(f"發生錯誤: {str(e)}")
    logging.error(f"當前 URL: {driver.current_url}")
    logging.info("程式異常結束，網站保持開啟")

finally:
    # 移除 driver.quit()，保持網站開啟
    logging.info("程式結束")
    if os.path.exists("captcha.png"):
        os.remove("captcha.png")