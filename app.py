import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_utils import YEARS, apply_theme, load_all_data, summarize_year


st.set_page_config(
    page_title="World Happiness Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

st.title("🌍 World Happiness Dashboard")
st.caption("Phân tích hạnh phúc toàn cầu 2015–2019")

data = load_all_data()
if data.empty:
    st.error("Không thể tải dữ liệu. Kiểm tra thư mục data.")
    st.stop()

with st.sidebar:
    st.header("Bộ lọc")
    selected_year = st.select_slider("Năm", options=YEARS, value=YEARS[-1])
    query = st.text_input("Tìm quốc gia", placeholder="Ví dụ: Finland")
    st.divider()
    st.caption("Dữ liệu chuẩn hóa và lưu cache trong 1 giờ.")

year_data = summarize_year(data, int(selected_year))
if query:
    year_data = year_data[
        year_data["Country"].str.contains(query, case=False, na=False)
    ]

top_score = year_data["Happiness Score"].max()
bottom_score = year_data["Happiness Score"].min()
average_score = year_data["Happiness Score"].mean()
top_country = (
    year_data.loc[year_data["Happiness Score"].idxmax(), "Country"]
    if not year_data.empty
    else "—"
)

metric_cols = st.columns(4)
metric_cols[0].metric("Quốc gia cao nhất", top_country)
metric_cols[1].metric(
    "Điểm cao nhất", f"{top_score:.3f}" if pd.notna(top_score) else "—"
)
metric_cols[2].metric(
    "Điểm trung bình", f"{average_score:.3f}" if pd.notna(average_score) else "—"
)
metric_cols[3].metric(
    "Điểm thấp nhất", f"{bottom_score:.3f}" if pd.notna(bottom_score) else "—"
)

tab_overview, tab_trends, tab_factors = st.tabs(
    ["📊 Tổng quan", "📈 Xu hướng", "🔎 Yếu tố"]
)

with tab_overview:
    chart_col, table_col = st.columns([1.5, 1])
    top10 = year_data.nlargest(10, "Happiness Score")

    with chart_col:
        fig = px.bar(
            top10.sort_values("Happiness Score"),
            x="Happiness Score",
            y="Country",
            orientation="h",
            color="Happiness Score",
            color_continuous_scale="Teal",
            title=f"Top 10 quốc gia hạnh phúc nhất — {selected_year}",
        )
        fig.update_layout(
            height=430,
            margin=dict(l=10, r=10, t=50, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        st.subheader("Bảng xếp hạng")
        st.dataframe(
            year_data[["Happiness Rank", "Country", "Happiness Score"]].head(20),
            use_container_width=True,
            hide_index=True,
            height=430,
        )

with tab_trends:
    trend = (
        data.groupby("Year", as_index=False)["Happiness Score"]
        .mean()
        .rename(columns={"Happiness Score": "Điểm trung bình"})
    )
    fig = px.line(
        trend,
        x="Year",
        y="Điểm trung bình",
        markers=True,
        title="Điểm hạnh phúc trung bình toàn cầu",
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

    country_options = sorted(data["Country"].dropna().unique())
    default_country = "Finland" if "Finland" in country_options else country_options[0]
    country = st.selectbox(
        "So sánh một quốc gia",
        country_options,
        index=country_options.index(default_country),
    )
    country_trend = data[data["Country"] == country]
    fig_country = px.line(
        country_trend,
        x="Year",
        y="Happiness Score",
        markers=True,
        title=f"Diễn biến điểm hạnh phúc của {country}",
    )
    fig_country.update_layout(height=360)
    st.plotly_chart(fig_country, use_container_width=True)

with tab_factors:
    factor = st.selectbox(
        "Yếu tố phân tích",
        [
            "GDP per capita",
            "Social support",
            "Life Expectancy",
            "Freedom",
            "Generosity",
            "Perceptions of corruption",
        ],
    )
    scatter_data = data.dropna(subset=[factor, "Happiness Score"])
    fig = px.scatter(
        scatter_data,
        x=factor,
        y="Happiness Score",
        color="Year",
        hover_name="Country",
        title=f"Mối quan hệ giữa {factor} và điểm hạnh phúc",
    )
    fig.update_layout(height=470)
    st.plotly_chart(fig, use_container_width=True)

    correlation = (
        data[
            [
                "Happiness Score",
                "GDP per capita",
                "Social support",
                "Life Expectancy",
                "Freedom",
                "Generosity",
                "Perceptions of corruption",
            ]
        ]
        .corr(numeric_only=True)["Happiness Score"]
        .drop("Happiness Score")
        .sort_values(ascending=False)
    )
    st.subheader("Tương quan với điểm hạnh phúc")
    st.dataframe(
        correlation.rename("Hệ số tương quan").to_frame(),
        use_container_width=True,
    )
