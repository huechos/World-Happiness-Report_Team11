<<<<<<< HEAD
# World Happiness Dashboard - Nhóm 11

Ứng dụng dashboard trực quan hóa dữ liệu **World Happiness Report** bằng
Streamlit, Pandas và Plotly. Dự án tập trung khám phá điểm hạnh phúc của các
quốc gia và mối liên hệ giữa điểm số này với những chỉ số kinh tế - xã hội.

## Dữ liệu

Dữ liệu CSV theo năm 2015–2019 được lưu trong thư mục `data/`. Các file có thể
dùng tên cột khác nhau giữa các năm; trang xu hướng chuẩn hóa một số tên cột
khi tải dữ liệu để phân tích nhất quán.

`preprocess.py` chuẩn hóa tên cột và xử lý giá trị thiếu. Lưu ý: script hiện
ghi kết quả trở lại các file CSV đầu vào trong `data/`. Hãy sao lưu dữ liệu gốc
trước khi chạy nếu cần giữ nguyên bản ban đầu.

## Cài đặt và chạy

Yêu cầu Python 3.10 trở lên.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Sau khi chạy, mở địa chỉ Local URL được Streamlit hiển thị trong terminal.

Nếu cần chuẩn hóa lại dữ liệu, chạy từ thư mục gốc dự án:

```powershell
python preprocess.py
```

## Các trang hiện có

- **Trang chủ (`app.py`)**: giới thiệu dự án và xem trước dữ liệu theo năm.
- **Overview (`pages/1_Overview.py`)**: chọn năm và xem nhanh dữ liệu của năm đó.
- **Trends (`pages/2_Trends.py`)**:
  - So sánh trung bình điểm hạnh phúc, GDP bình quân đầu người và tuổi thọ
    khỏe mạnh theo năm.
  - Xem area chart điểm hạnh phúc trung bình qua các năm.
  - Xem scatter plot giữa điểm hạnh phúc và GDP hoặc tuổi thọ, lọc theo năm,
    xem hệ số tương quan Pearson.
  - Tên quốc gia và năm được hiển thị khi rê chuột lên điểm dữ liệu.

Các trang Regional Analysis, Key Factors và Advanced Insights hiện chưa có
nội dung triển khai.

## Cấu trúc dự án

```text
.
├── app.py
├── preprocess.py
├── requirements.txt
├── data/
│   ├── 2015.csv
│   ├── 2016.csv
│   ├── 2017.csv
│   ├── 2018.csv
│   └── 2019.csv
└── pages/
    ├── 1_Overview.py
    ├── 2_Trends.py
    ├── 3_Regional_Analysis.py
    ├── 4_Key_Factors.py
    └── 5_Advanced_Insights.py
```