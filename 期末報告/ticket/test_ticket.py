from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# 設定 ChromeDriver 路徑
CHROMEDRIVER_PATH = r"D:\Cent Brower\chromedriver-win64\chromedriver.exe"  # 請替換為您的 ChromeDriver 路徑

# 設定 Chrome 選項
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # 最大化視窗
# chrome_options.add_argument("--headless")  # 若不需顯示瀏覽器，取消註解此行

# 初始化 WebDriver
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 步驟 1：開啟寬宏售票網站
    driver.get("https://kham.com.tw/application/utk01/UTK0101_03.aspx")
    print("已開啟寬宏售票網站")

    # 步驟 2：搜尋活動（假設輸入框和按鈕的選擇器）
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search-input"))  # 請根據實際網站調整 ID
    )
    search_box.send_keys("演唱會名稱")  # 替換為您想搶的活動名稱
    search_button = driver.find_element(By.CLASS_NAME, "search-button")  # 請根據實際網站調整
    search_button.click()
    print("已搜尋活動")

    # 步驟 3：點擊活動連結
    event_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '演唱會名稱')]"))  # 調整 XPath
    )
    event_link.click()
    print("已進入活動頁面")

    # 步驟 4：選擇票價區域
    ticket_area = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'NT$1800')]"))  # 選擇票價
    )
    ticket_area.click()
    print("已選擇票價區域")

    # 步驟 5：選擇票數
    ticket_quantity = driver.find_element(By.ID, "ticket-quantity")  # 調整 ID
    ticket_quantity.send_keys("2")  # 選擇 2 張票
    print("已選擇票數")

    # 步驟 6：點擊「立即購票」
    buy_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "buy-ticket-button"))  # 調整 ID
    )
    buy_button.click()
    print("已點擊立即購票")

    # 步驟 7：填寫購買者資訊
    name_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "name"))  # 調整 ID
    )
    name_input.send_keys("您的姓名")
    
    phone_input = driver.find_element(By.ID, "phone")  # 調整 ID
    phone_input.send_keys("您的手機號碼")
    
    email_input = driver.find_element(By.ID, "email")  # 調整 ID
    email_input.send_keys("您的電子郵件")
    print("已填寫購買者資訊")

    # 步驟 8：提交訂單
    submit_button = driver.find_element(By.ID, "submit-order")  # 調整 ID
    submit_button.click()
    print("已提交訂單")

    # 等待確認頁面（可根據需求調整）
    time.sleep(5)

finally:
    # 關閉瀏覽器
    driver.quit()
    print("程式結束")