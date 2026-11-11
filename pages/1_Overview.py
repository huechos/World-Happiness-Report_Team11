import streamlit as st
import pandas as pd

st.title("📊 Phân tích theo từng năm độc lập")

# Tạo một selectbox chọn năm ở sidebar hoặc ngay trên trang
selected_year = st.selectbox("Chọn năm báo cáo:", [2015, 2016, 2017, 2018])

# Load dữ liệu tương ứng với năm được chọn
@st.cache_data
def load_data_by_year(year):
    file_path = f"data/{year}.csv"
    return pd.read_csv(file_path)

df = load_data_by_year(selected_year)

st.write(f"Đang hiển thị dữ liệu của năm **{selected_year}** (Tổng số quốc gia: {len(df)})")
st.dataframe(df.head())