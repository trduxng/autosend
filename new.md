Tin vui cho bạn là thư viện schedule trong đoạn code trước đã mặc định có tính năng lặp lại hàng ngày (daily loop) rồi.

Câu lệnh schedule.every().day.at(...) nghĩa là: "Cứ đến giờ này mỗi ngày thì làm, làm xong thì hẹn lại giờ đó ngày mai".

Tuy nhiên, để tool chạy bền bỉ, liên tục nhiều ngày, không bị văng (crash) nếu lỡ mạng rớt hoặc lỗi bất ngờ, tôi sẽ nâng cấp code thêm cơ chế "Bắt lỗi an toàn" (Safe Guard).

Dưới đây là phiên bản "Treo máy vĩnh viễn", bạn có thể để nó chạy cả tháng cũng được.
File: autosend_loop_final.py
Python

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

Hướng dẫn chạy "Bất Tử" trên Debian

Vì bạn dùng Linux, nếu bạn chạy lệnh python3 autosend_loop_final.py rồi tắt cửa sổ Terminal đi, tool sẽ tắt theo.

Để tool chạy mãi mãi (kể cả khi bạn tắt máy tính remote), bạn phải dùng nohup hoặc tmux.
Cách 1: Dùng nohup (Đơn giản nhất)

Chạy lệnh này trong Terminal:
Bash

nohup python3 autosend_loop_final.py > output.log 2>&1 &

    nohup ... &: Chạy lệnh trong nền, không bị tắt khi đóng terminal.

    > output.log: Mọi dòng chữ print sẽ được ghi vào file output.log thay vì hiện lên màn hình.

Kiểm tra tool đang chạy không:
Bash

ps aux | grep python

Tắt tool:
Bash

pkill -f autosend_loop_final.py

Cách 2: Dùng tmux (Khuyên dùng cho dân Linux)

tmux tạo ra một cửa sổ ảo. Bạn vào đó chạy tool, rồi "thoát ra" (detach) nhưng cửa sổ đó vẫn chạy ngầm.

    Cài tmux: sudo apt install tmux

    Tạo session mới: tmux new -s zalo_bot

    Chạy code: python3 autosend_loop_final.py

    Thoát ra ngoài (nhưng tool vẫn chạy): Bấm Ctrl+B, thả tay ra, rồi bấm phím D.

    Khi nào muốn vào xem lại: tmux attach -t zalo_bot

Tính năng mới trong bản Code này:

    Ghi Log (history_autosend.log): Giúp bạn kiểm tra lại lịch sử. Ví dụ sáng mai ngủ dậy bạn mở file này ra xem: "À, lúc 7:00 sáng nay nó đã gửi thành công cho Vợ Yêu".

    Try/Catch bao bọc: Nếu hôm nay mạng rớt khiến việc gửi tin lúc 7:00 thất bại, tool không bị dừng lại. Nó sẽ bỏ qua lỗi đó và tiếp tục chờ đến 8:30 để gửi tin tiếp theo.

    Tự động lặp lại: Hàm schedule.every().day đảm bảo sau khi gửi xong hôm nay, nó tự hẹn giờ cho ngày mai.
