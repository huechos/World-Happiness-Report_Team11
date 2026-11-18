import plotly.express as px
import streamlit as st

from dashboard_utils import YEARS, apply_theme, load_all_data, summarize_year


st.set_page_config(page_title="Tổng quan", page_icon="📊", layout="wide")
apply_theme()
st.title("📊 Tổng quan theo năm")

data = load_all_data()
selected_year = st.select_slider("Chọn năm", options=YEARS, value=YEARS[-1])
year_data = summarize_year(data, int(selected_year))

tab_table, tab_distribution = st.tabs(["📋 Dữ liệu", "📦 Phân bố"])

with tab_table:
    st.caption(f"{len(year_data)} quốc gia trong năm {selected_year}")
    st.dataframe(
        year_data.sort_values("Happiness Rank"),
        use_container_width=True,
        hide_index=True,
        height=560,
    )
    st.download_button(
        "Tải CSV",
        year_data.to_csv(index=False).encode("utf-8"),
        file_name=f"happiness-{selected_year}.csv",
        mime="text/csv",
    )

with tab_distribution:
    fig = px.histogram(
        year_data,
        x="Happiness Score",
        nbins=20,
        marginal="box",
        title=f"Phân bố điểm hạnh phúc — {selected_year}",
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)