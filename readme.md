Hướng dẫn chạy "Bất Tử" trên Debian

Vì bạn dùng Linux, nếu bạn chạy lệnh python3 autosend_loop_final.py rồi tắt cửa sổ Terminal đi, tool sẽ tắt theo.

Để tool chạy mãi mãi (kể cả khi bạn tắt máy tính remote), bạn phải dùng nohup hoặc tmux.
Cách 1: Dùng nohup (Đơn giản nhất)

Chạy lệnh này trong Terminal:
Bash: nohup python3 autosend_loop_final.py > output.log 2>&1 &

    - nohup ... &: Chạy lệnh trong nền, không bị tắt khi đóng terminal.
    - > output.log: Mọi dòng chữ print sẽ được ghi vào file output.log thay vì hiện lên màn hình.

Kiểm tra tool đang chạy không:
Bash: ps aux | grep python

Tắt tool:
Bash: pkill -f autosend_loop_final.py

Cách 2: Dùng tmux (Khuyên dùng cho dân Linux)

tmux tạo ra một cửa sổ ảo. Bạn vào đó chạy tool, rồi "thoát ra" (detach) nhưng cửa sổ đó vẫn chạy ngầm.

    1. Cài tmux: sudo apt install tmux

    2. Tạo session mới: tmux new -s zalo_bot

    3. Chạy code: python3 autosend_loop_final.py

    4. Thoát ra ngoài (nhưng tool vẫn chạy): Bấm Ctrl+B, thả tay ra, rồi bấm phím D.

    5. Khi nào muốn vào xem lại: tmux attach -t zalo_bot

Tính năng mới trong bản Code này:

    1. Ghi Log (history_autosend.log): Giúp bạn kiểm tra lại lịch sử. Ví dụ sáng mai ngủ dậy bạn mở file này ra xem: "À, lúc 7:00 sáng nay nó đã gửi thành công cho Vợ Yêu".

    2. Try/Catch bao bọc: Nếu hôm nay mạng rớt khiến việc gửi tin lúc 7:00 thất bại, tool không bị dừng lại. Nó sẽ bỏ qua lỗi đó và tiếp tục chờ đến 8:30 để gửi tin tiếp theo.

    3. Tự động lặp lại: Hàm schedule.every().day đảm bảo sau khi gửi xong hôm nay, nó tự hẹn giờ cho ngày mai.
