import os
import time

# Ép hệ thống Python dùng giờ Việt Nam
os.environ['TZ'] = 'Asia/Ho_Chi_Minh'
time.tzset()

print("Thời gian hiện tại:", time.strftime('%X'))