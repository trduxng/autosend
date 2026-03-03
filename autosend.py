import time
import os
import schedule
import pyperclip
import logging # Thêm ghi log để theo dõi lịch sử chạy lâu dài
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ================= CẤU HÌNH LỊCH (SỬA Ở ĐÂY) =================
# Tool sẽ tự động lặp lại các giờ này VÀO NGÀY HÔM SAU
DANH_SACH_LICH = [
    {"time": "07:00", "name": "Vợ Yêu", "msg": "Chúc vợ ngày mới tốt lành!"},
    {"time": "08:30", "name": "Nhóm Chat Công Việc", "msg": "Mọi người check mail nhé."},
    {"time": "11:30", "name": "Bạn Thân", "msg": "Đi ăn cơm không?"},
    # Thêm bao nhiêu tùy thích...
]

PROFILE_PATH = "/home/trduxng/.mozilla/firefox/ji9q0gsu.default"
# =============================================================

# Cấu hình ghi log ra file (để bạn kiểm tra lại xem hôm qua có gửi được không)
logging.basicConfig(filename='history_autosend.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def gui_tin_zalo(ten_nguoi_nhan, noi_dung):
    print(f"\n⚡ [KÍCH HOẠT] Đến giờ gửi cho: {ten_nguoi_nhan}")
    
    if not os.path.exists(PROFILE_PATH):
        print("❌ LỖI: Sai đường dẫn Profile!")
        logging.error(f"Thất bại gửi cho {ten_nguoi_nhan}: Sai Profile")
        return

    options = Options()
    options.add_argument("-profile")
    options.add_argument(PROFILE_PATH)
    
    # --- QUAN TRỌNG: HEADLESS ---
    # Khi treo máy chạy ngầm lâu dài trên Linux (Server/VPS), 
    # nên bật chế độ không giao diện (headless) để đỡ tốn RAM.
    # Nếu chạy máy cá nhân muốn xem thì đóng comment dòng dưới lại.
    # options.add_argument("--headless") 

    driver = None
    try:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 60) # Tăng thời gian chờ lên 60s cho mạng chậm
        actions = ActionChains(driver)

        driver.get("https://chat.zalo.me/")
        time.sleep(20) # Chờ lâu hơn chút cho chắc

        # 1. TÌM KIẾM
        try:
            search_box = wait.until(EC.element_to_be_clickable((By.ID, "contact-search-input")))
        except:
            search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Tìm kiếm']")))

        search_box.click()
        actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()
        time.sleep(1)
        
        pyperclip.copy(ten_nguoi_nhan)
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        
        time.sleep(5) # Chờ gợi ý hiện ra
        
        # Chọn người
        actions.send_keys(Keys.ARROW_DOWN).pause(0.5).send_keys(Keys.ENTER).perform()
        time.sleep(5)

        # 2. GỬI TIN
        try:
            chat_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.rich-input")))
        except:
            chat_box = driver.find_element(By.ID, "richInput")

        chat_box.click()
        time.sleep(1)

        pyperclip.copy(noi_dung) 
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(2)
        
        actions.send_keys(Keys.ENTER).perform()
        
        msg_success = f"✅ GỬI THÀNH CÔNG: {ten_nguoi_nhan} | Nội dung: {noi_dung}"
        print(msg_success)
        logging.info(msg_success) # Ghi vào file log

    except Exception as e:
        msg_error = f"❌ THẤT BẠI gửi cho {ten_nguoi_nhan}. Lỗi: {str(e)}"
        print(msg_error)
        logging.error(msg_error)
        # Chụp ảnh lỗi để debug sau này
        if driver:
            try:
                driver.save_screenshot(f"error_{datetime.now().strftime('%Y%m%d_%H%M')}.png")
            except:
                pass

    finally:
        if driver:
            print("🏁 Đóng trình duyệt, chờ lượt tiếp theo...")
            time.sleep(5)
            try:
                driver.quit()
            except:
                pass # Bỏ qua lỗi khi đóng driver

def job_wrapper(job_info):
    """Hàm bọc để bắt lỗi, đảm bảo 1 job chết không làm chết cả tool"""
    try:
        gui_tin_zalo(job_info['name'], job_info['msg'])
    except Exception as e:
        print(f"⚠️ Lỗi nghiêm trọng ở vòng lặp ngoài: {e}")

# ================= MAIN LOOP =================
def chay_vinh_vien():
    print(f"🐧 TOOL AUTO ZALO ĐANG CHẠY TRÊN DEBIAN...")
    print(f"🕒 Thời gian hiện tại: {datetime.now().strftime('%H:%M:%S')}")
    print("-------------------------------------------------")
    
    # Đăng ký lịch
    for job in DANH_SACH_LICH:
        # Lưu ý kỹ thuật: dùng default argument (j=job) để tránh lỗi closure trong vòng lặp
        schedule.every().day.at(job['time']).do(job_wrapper, job_info=job)
        print(f"📅 Đã lên lịch: {job['time']} -> {job['name']}")

    print("-------------------------------------------------")
    print("💤 Đang chạy ngầm. Bấm Ctrl+C để dừng (nếu chạy foreground).")

    while True:
        try:
            # Kiểm tra lịch mỗi phút
            schedule.run_pending()
            
            # In ra màn hình cho biết tool vẫn sống (tùy chọn)
            # print(".", end="", flush=True) 
            
            time.sleep(30) # Ngủ 30s để đỡ tốn CPU
            
        except KeyboardInterrupt:
            print("\n🛑 Đã dừng tool thủ công.")
            break
        except Exception as e:
            print(f"\n⚠️ Lỗi vòng lặp chính: {e}. Đang tự khởi động lại sau 1 phút...")
            time.sleep(60)

if __name__ == "__main__":
    chay_vinh_vien()
