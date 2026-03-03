import time
import os
import pyperclip
from datetime import datetime  # Thư viện xử lý thời gian
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ================= CẤU HÌNH HẸN GIỜ =================
# Định dạng 24h (Giờ:Phút). Ví dụ: "07:30", "14:05", "22:00"
# Nếu muốn gửi NGAY LẬP TỨC, hãy để trống: THOI_GIAN_GUI = ""
THOI_GIAN_GUI = "05:50" 
# THOI_GIAN_GUI = "" 

# Thông tin người nhận & Nội dung
# TEN_NGUOI_NHAN = "My Documents"
TEN_NGUOI_NHAN = "Báo Thức Đầu Năm"

NOI_DUNG_TIN = "toi an toan"

# Đường dẫn Profile Firefox (Copy từ bài trước của bạn)
PROFILE_PATH = "/home/trduxng/snap/firefox/common/.mozilla/firefox/740e7bqe.default"
# ====================================================

def gui_tin_zalo():
    print(f"\n🚀 ĐANG THỰC HIỆN GỬI TIN LÚC {datetime.now().strftime('%H:%M:%S')}...")
    
    if not os.path.exists(PROFILE_PATH):
        print(f"❌ LỖI: Không tìm thấy thư mục Profile!")
        return

    options = Options()
    options.add_argument("-profile")
    options.add_argument(PROFILE_PATH)
    
    # Chạy ngầm (Headless) nếu muốn không hiện cửa sổ lên:
    # options.add_argument("--headless") 

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 40)
    actions = ActionChains(driver)

    try:
        driver.get("https://chat.zalo.me/")
        print("⏳ Đang tải Zalo Web (15s)...")
        time.sleep(15) 

        # --- BƯỚC 1: TÌM NGƯỜI ---
        print("🔍 Đang tìm ô Search...")
        try:
            search_box = wait.until(EC.element_to_be_clickable((By.ID, "contact-search-input")))
        except:
            search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Tìm kiếm']")))

        search_box.click()
        
        # Xóa text cũ
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()
        time.sleep(0.5)

        # Nhập tên
        print(f"⌨️ Nhập tên: {TEN_NGUOI_NHAN}")
        pyperclip.copy(TEN_NGUOI_NHAN)
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        
        print("⏳ Chờ gợi ý hiện ra (3s)...")
        time.sleep(3) 
        
        print("⬇️ Chọn người đầu tiên...")
        actions.send_keys(Keys.ARROW_DOWN).pause(0.5).send_keys(Keys.ENTER).perform()
        
        print("✅ Đã vào khung chat. Đang chờ load...")
        time.sleep(3)

        # --- BƯỚC 2: GỬI TIN ---
        print("✍️ Đang tìm ô nhập tin nhắn...")
        try:
            chat_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.rich-input")))
        except:
            chat_box = driver.find_element(By.ID, "richInput")

        chat_box.click()
        time.sleep(1)

        # Copy & Paste nội dung
        pyperclip.copy(NOI_DUNG_TIN) 
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)
        
        print("🚀 Đang nhấn Enter để gửi...")
        actions.send_keys(Keys.ENTER).perform()
        
        print(f"🎉 ĐÃ GỬI THÀNH CÔNG VÀO LÚC {datetime.now().strftime('%H:%M:%S')}!")
        time.sleep(5)


    except Exception as e:
        print(f"❌ CÓ LỖI XẢY RA: {e}")
        driver.save_screenshot("error_timer.png")
    finally:
        print("🏁 Đóng trình duyệt sau 5s.")
        time.sleep(5)
        driver.quit()

def che_do_cho():
    """Hàm kiểm tra thời gian liên tục"""
    if THOI_GIAN_GUI == "":
        print("⚡ Chế độ gửi ngay lập tức!")
        gui_tin_zalo()
        return

    print(f"⏰ Đang chạy chế độ Hẹn Giờ.")
    print(f"👉 Tool sẽ đợi đến: {THOI_GIAN_GUI}")
    print(f"👉 Thời gian hiện tại: {datetime.now().strftime('%H:%M:%S')}")
    print("------------------------------------------------")

    while True:
        # Lấy giờ phút hiện tại (ví dụ: "09:20")
        now = datetime.now().strftime("%H:%M")
        
        if now == THOI_GIAN_GUI:
            print("\n🔔 ĐING BOONG! ĐÃ ĐẾN GIỜ GỬI TIN!")
            gui_tin_zalo()
            break # Thoát vòng lặp sau khi gửi xong
        
        # Chờ 20 giây rồi kiểm tra lại (để đỡ tốn CPU)
        time.sleep(20)

if __name__ == "__main__":
    try:
        che_do_cho()
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng chương trình.")