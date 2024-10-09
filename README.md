```markdown
# Dự Án Chuyển Đổi Video Tự Động

Dự án này được thiết kế để tự động chuyển đổi các tệp video từ định dạng `.mpg` sang định dạng `.mp4` sử dụng `ffmpeg` với codec `h264_nvenc`. Hệ thống sẽ đồng bộ hóa các thư mục đầu vào và đầu ra, xử lý chuyển đổi video, và tự động xóa các tệp cũ để tiết kiệm không gian lưu trữ.

## Nội Dung

- [Yêu Cầu](#yêu-cầu)
- [Cài Đặt](#cài-đặt)
- [Cấu Hình](#cấu-hình)
- [Sử Dụng](#sử-dụng)
- [Giám Sát và Bảo Trì](#giám-sát-và-bảo-trì)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Giấy Phép](#giấy-phép)

## Yêu Cầu

- **Hệ Điều Hành:** Linux
- **Python:** 3.8 trở lên
- **FFmpeg:** Phiên bản hỗ trợ `h264_nvenc`
- **rsync:** Được cài đặt trên hệ thống
- **Thư viện Python:** Xem trong `requirements.txt`

## Cài Đặt

1. **Cài Đặt Python và pip:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Cài Đặt FFmpeg:**
   ```bash
   sudo apt install ffmpeg
   ```

   **Lưu ý:** Đảm bảo FFmpeg được biên dịch với hỗ trợ `h264_nvenc`. Bạn có thể kiểm tra bằng lệnh:
   ```bash
   ffmpeg -encoders | grep nvenc
   ```

3. **Cài Đặt rsync:**
   ```bash
   sudo apt install rsync
   ```

4. **Cài Đặt Thư Viện Python:**
   Trong thư mục dự án, chạy:
   ```bash
   pip3 install -r requirements.txt
   ```

## Cấu Hình

Cấu hình dự án được lưu trong file `config.json`. Dưới đây là mẫu cấu hình:

```json
{
    "input_dirs": [
        "/mnt/cho_duyet/THU_2",
        "/mnt/cho_duyet/THU_3",
        "/mnt/cho_duyet/THU_4",
        "/mnt/cho_duyet/THU_5",
        "/mnt/cho_duyet/THU_6",
        "/mnt/cho_duyet/THU_7",
        "/mnt/cho_duyet/CN"
    ],
    "output_dirs": [
        "/mnt/mobile/THU_2",
        "/mnt/mobile/THU_3",
        "/mnt/mobile/THU_4",
        "/mnt/mobile/THU_5",
        "/mnt/mobile/THU_6",
        "/mnt/mobile/THU_7",
        "/mnt/mobile/CN"
    ],
    "log_file": "converted_files.log",
    "time_interval": 600,
    "days_old": 3
}
```

- **input_dirs:** Danh sách các thư mục chứa video cần chuyển đổi.
- **output_dirs:** Danh sách các thư mục đầu ra sau khi chuyển đổi.
- **log_file:** File log để lưu trữ các tệp đã được chuyển đổi.
- **time_interval:** Khoảng thời gian giữa các chu kỳ xử lý (tính bằng giây).
- **days_old:** Số ngày để xóa các tệp cũ trong thư mục đầu ra.

## Sử Dụng

### 1. Đảm Bảo Các Thư Mục Đã Được Đồng Bộ

Trước khi chạy script, hãy đảm bảo rằng các thư mục đầu vào và đầu ra đã được đồng bộ hóa bằng cách sử dụng `rsync` hoặc các công cụ đồng bộ khác.

### 2. Chạy Script Chuyển Đổi Video

Bạn có thể chạy script Python trực tiếp hoặc thiết lập nó dưới dạng một dịch vụ để tự động chạy nền.

#### Chạy Thủ Công

```bash
python3 transcode_script.py
```

#### Chạy Dưới Dạng Dịch Vụ với systemd

1. **Tạo File Service:**

   Tạo file `transcode.service` trong thư mục `/etc/systemd/system/` với nội dung sau:

   ```ini
   [Unit]
   Description=Transcode Service
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /home/khanhvo/hgtv-transcode/transcode_script.py
   WorkingDirectory=/home/khanhvo/hgtv-transcode
   StandardOutput=inherit
   StandardError=inherit
   Restart=always
   User=khanhvo
   Group=khanhvo

   [Install]
   WantedBy=multi-user.target
   ```

2. **Kích Hoạt Và Bắt Đầu Service:**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start transcode.service
   sudo systemctl enable transcode.service
   ```

3. **Kiểm Tra Service:**

   ```bash
   sudo systemctl status transcode.service
   ```

### 3. Chạy Script với `nohup`

Nếu bạn không muốn sử dụng systemd, có thể chạy script dưới dạng nền bằng `nohup`:

```bash
nohup python3 transcode_script.py > transcode.log 2>&1 &
```

## Giám Sát và Bảo Trì

- **Xem Log Chuyển Đổi:**
  ```bash
  tail -f converted_files.log
  ```

- **Xem Log Dịch Vụ (nếu sử dụng systemd):**
  ```bash
  journalctl -u transcode.service -f
  ```

- **Xóa Các Tệp Cũ Trong Thư Mục Đầu Ra:**
  Hệ thống sẽ tự động xóa các tệp cũ dựa trên giá trị `days_old` trong `config.json`. Bạn cũng có thể thực hiện thủ công nếu cần.

## Cấu Trúc Dự Án

```plaintext
hgtv-transcode/
├── config.json
├── converted_files.log
├── transcode_script.py
├── transcode.service
├── transcode_script.spec
├── requirements.txt
├── sync.sh
└── README.md
```

- **config.json:** File cấu hình chính cho dự án.
- **converted_files.log:** File log lưu trữ tên các tệp đã được chuyển đổi.
- **transcode_script.py:** Script Python chính xử lý chuyển đổi video.
- **transcode.service:** File service để chạy script dưới dạng dịch vụ systemd.
- **transcode_script.spec:** File cấu hình cho PyInstaller.
- **requirements.txt:** Danh sách các thư viện Python cần thiết.
- **sync.sh:** Script đồng bộ hóa thư mục (nếu có).
- **README.md:** File hướng dẫn này.

## Giấy Phép

Dự án này được phát hành dưới [MIT License](LICENSE).

---

© 2024 Khanh Vo. Bảo lưu mọi quyền.
```