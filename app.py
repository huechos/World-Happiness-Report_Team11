import streamlit as st
import pandas as pd
import os

# 1. Cấu hình trang chủ (Phải đặt ở dòng đầu tiên của file)
st.set_page_config(
    page_title="World Happiness Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Tiêu đề chính của ứng dụng
st.title("🌍 Hệ thống Trực quan hóa Dữ liệu: Báo cáo Hạnh phúc Toàn cầu")
st.markdown("### Đề tài: Phân tích các yếu tố ảnh hưởng đến Chỉ số Hạnh phúc các Quốc gia")
st.write("---")

# 3. Phần giới thiệu dự án (Introduction)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 🎯 Giới thiệu chung
    Chào mừng bạn đến với ứng dụng Dashboard phân tích dữ liệu **World Happiness Report**. 
    Ứng dụng được thiết kế nhằm giúp người xem khám phá và đánh giá sự chênh lệch về mức độ hạnh phúc giữa các quốc gia, 
    đồng thời tìm hiểu mối tương quan với các chỉ số kinh tế - xã hội quan trọng như:
    - **GDP bình quân đầu ngời (GDP per capita)**
    - **Sự hỗ trợ xã hội (Social support)**
    - **Tuổi thọ khỏe mạnh (Life Expectancy)**
    - **Quyền tự do cá nhân (Freedom)**
    - **Mức độ minh bạch / nhận thức tham nhũng (Perceptions of corruption)**
    """)

with col2:
    st.info("""
    **Thông tin nhóm thực hiện:**
    - **Tên nhóm:** Nhóm 11
    - **Môn học:** Trực quan hóa Dữ liệu
    - **Lớp:** KHMT 18-01 (Đại học Đại Nam)
    - **Công cụ:** Python, Pandas, Plotly, Streamlit
    """)

st.write("---")

# 4. Hướng dẫn sử dụng điều hướng
st.subheader("🧭 Hướng dẫn điều hướng Dashboard")
st.markdown("""
Sử dụng **Thanh điều hướng (Sidebar)** ở bên trái màn hình để di chuyển qua các trang phân tích chi tiết:
1. **Overview (Tổng quan):** Xem các chỉ số KPI toàn cầu và bảng dữ liệu gốc theo từng năm.
2. **Trends (Xu hướng & Tương quan):** Khám phá sự thay đổi qua thời gian và mối quan hệ giữa các biến.
3. **Regional Analysis (Phân tích khu vực):** So sánh điểm số hạnh phúc giữa các châu lục, khu vực khác nhau.
4. **Key Factors (Yếu tố tác động):** Đào sâu vào các nhóm nhân tố cốt lõi quyết định độ hạnh phúc.
5. **Advanced Insights (Khám phá nâng cao):** Trải nghiệm giao diện tương tác nâng cao, bộ lọc và các nhận xét kết luận.
""")

st.write("---")

# 5. Thêm phần xem trước dữ liệu nhanh ngay tại trang chủ để tạo điểm nhấn
st.subheader("📂 Kiểm tra trạng thái dữ liệu nhanh")

selected_year_preview = st.selectbox("Chọn năm dữ liệu muốn xem trước:", [2015, 2016, 2017, 2018, 2019])
preview_file_path = f"data/{selected_year_preview}.csv"

if os.path.exists(preview_file_path):
    df_preview = pd.read_csv(preview_file_path)
    st.success(f"Đã tải thành công file dữ liệu năm {selected_year_preview} ({len(df_preview)} quốc gia, {len(df_preview.columns)} cột).")
    
    with st.expander(f"Xem trước 5 dòng đầu tiên của dữ liệu năm {selected_year_preview}"):
        st.dataframe(df_preview.head(), use_container_width=True)
else:
    st.warning(f"⚠️ Chưa tìm thấy file `{preview_file_path}`. Hãy đảm bảo bạn đã chạy file `preprocess.py` để tạo các file dữ liệu sạch trước nhé!")

# Chân trang (Footer)
st.write("---")
st.markdown("<p style='text-align: center; color: gray;'>Phát triển bởi Nhóm 11 KHMT 18-01 - Đại học Đại Nam | 2026</p>", unsafe_allow_html=True)