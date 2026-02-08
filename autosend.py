import time
import os
import pyperclip  # Thư viện quản lý Clipboard (Copy/Paste)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ================= CẤU HÌNH NGƯỜI DÙNG =================
# Tên người nhận (Phải chính xác như trong danh bạ Zalo)
# --- CẤU HÌNH ---
TEN_NGUOI_NHAN = "My Documents" 
# Nội dung tin nhắn muốn gửi
NOI_DUNG_TIN = "Đây là tin nhắn tự động từ Debian (Final Version)"# Kiểm tra lại đường dẫn profile của bạn
PROFILE_PATH = "/home/trduxng/.mozilla/firefox/ji9q0gsu.default"


def gui_tin_zalo_bat_tu():
    print("🐧 Đang khởi động Tool trên Debian...")
    print(f"📂 Profile đang dùng: {PROFILE_PATH}")

    # 1. Kiểm tra đường dẫn Profile
    if not os.path.exists(PROFILE_PATH):
        print(f"❌ LỖI: Không tìm thấy thư mục Profile!")
        print("👉 Hãy kiểm tra lại đường dẫn trong 'about:profiles'")
        return

    # 2. Cấu hình Firefox
    options = Options()
    options.add_argument("-profile")
    options.add_argument(PROFILE_PATH)
    
    # Khởi tạo Driver
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    
    # Khởi tạo các công cụ hỗ trợ
    wait = WebDriverWait(driver, 40) # Chờ tối đa 40s
    actions = ActionChains(driver)   # Bàn phím ảo

    try:
        # 3. Mở Zalo Web
        driver.get("https://chat.zalo.me/")
        print("⏳ Đang đợi Zalo Web tải (15s)...")
        time.sleep(15) # Thời gian chờ cứng để Zalo load xong script

        # ---------------------------------------------------------
        # BƯỚC 4: TÌM KIẾM NGƯỜI DÙNG (Kỹ thuật Anti-Stale)
        # ---------------------------------------------------------
        print("🔍 Đang tìm ô Search...")
        
        try:
            # Tìm ô search bằng ID hoặc Placeholder
            search_box = wait.until(EC.element_to_be_clickable((By.ID, "contact-search-input")))
        except:
            search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Tìm kiếm']")))

        # Click vào ô search để lấy Focus
        search_box.click()
        
        # Xóa nội dung cũ (nếu có) bằng Ctrl+A -> Delete
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()
        time.sleep(0.5)

        # Nhập tên người nhận (Dùng Paste để tránh lỗi bộ gõ tiếng Việt)
        print(f"⌨️ Nhập tên: {TEN_NGUOI_NHAN}")
        pyperclip.copy(TEN_NGUOI_NHAN)
        
        # Paste tên vào
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        
        # --- QUAN TRỌNG NHẤT ---
        # Sau khi paste, Zalo sẽ load lại danh sách gợi ý.
        # Ta KHÔNG click vào kết quả, mà dùng bàn phím để chọn.
        print("⏳ Chờ gợi ý hiện ra (3s)...")
        time.sleep(3) 
        
        print("⬇️ Dùng phím Mũi Tên để chọn người đầu tiên...")
        # Nhấn Mũi Tên Xuống (Chọn người đầu tiên) -> Nhấn Enter (Vào chat)
        actions.send_keys(Keys.ARROW_DOWN).pause(0.5).send_keys(Keys.ENTER).perform()
        
        print("✅ Đã vào khung chat. Đang chờ load...")
        time.sleep(3) # Chờ khung chat load xong

        # ---------------------------------------------------------
        # BƯỚC 5: NHẬP VÀ GỬI TIN NHẮN
        # ---------------------------------------------------------
        print("✍️ Đang tìm ô nhập tin nhắn...")
        
        try:
            # Tìm ô nhập liệu (thường là thẻ div rich-input)
            chat_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.rich-input")))
        except:
            # Dự phòng
            chat_box = driver.find_element(By.ID, "richInput")

        # Click để lấy focus vào ô chat
        chat_box.click()
        time.sleep(0.5)

        # Copy nội dung tin nhắn vào Clipboard
        pyperclip.copy(NOI_DUNG_TIN)
        
        # Paste nội dung (Ctrl + V)
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        
        # Chờ 1 chút để Zalo nhận diện văn bản
        time.sleep(1)
        
        # Nhấn Enter để gửi (Dùng ActionChains thay vì element.send_keys)
        print("🚀 Đang nhấn Enter để gửi...")
        actions.send_keys(Keys.ENTER).perform()
        
        print(f"🎉 GỬI THÀNH CÔNG CHO: {TEN_NGUOI_NHAN}")
        print(f"Nội dung: {NOI_DUNG_TIN}")

    except Exception as e:
        print(f"❌ CÓ LỖI XẢY RA: {e}")
        # Chụp màn hình lỗi để debug
        driver.save_screenshot("error_cuoi_cung.png")
        print("📸 Đã lưu ảnh lỗi tại: error_cuoi_cung.png")
        
    finally:
        print("🏁 Hoàn tất. Đóng trình duyệt sau 5s.")
        time.sleep(5)
        driver.quit()

# Chạy chương trình
if __name__ == "__main__":
    gui_tin_zalo_bat_tu()