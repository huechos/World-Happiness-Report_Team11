import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_utils import YEARS, apply_theme, load_all_data


st.set_page_config(
    page_title="Khám phá nâng cao",
    page_icon="🔎",
    layout="wide",
)
apply_theme()

st.title("🔎 Khám phá nâng cao")
st.caption("Lọc, so sánh và tìm hiểu các yếu tố liên quan đến hạnh phúc.")


@st.cache_data(ttl=900)
def filter_data(years, score_min, score_max, country_query):
    data = load_all_data()
    filtered = data[
        data["Year"].isin(years)
        & data["Happiness Score"].between(score_min, score_max)
    ]
    if country_query:
        filtered = filtered[
            filtered["Country"].str.contains(
                country_query, case=False, na=False, regex=False
            )
        ]
    return filtered


data = load_all_data()
if data.empty:
    st.error("Không thể tải dữ liệu. Kiểm tra thư mục data.")
    st.stop()

score_min = float(data["Happiness Score"].min())
score_max = float(data["Happiness Score"].max())

with st.sidebar:
    st.header("Bộ lọc dữ liệu")
    selected_years = st.multiselect("Năm báo cáo", YEARS, default=YEARS)
    score_range = st.slider(
        "Khoảng điểm hạnh phúc",
        min_value=score_min,
        max_value=score_max,
        value=(score_min, score_max),
        step=0.1,
    )
    country_query = st.text_input(
        "Tìm quốc gia",
        placeholder="Nhập tên quốc gia",
    )

filtered = filter_data(
    tuple(selected_years),
    score_range[0],
    score_range[1],
    country_query.strip(),
)

if filtered.empty:
    st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    st.stop()

factor_options = [
    "GDP per capita",
    "Social support",
    "Life Expectancy",
    "Freedom",
    "Generosity",
    "Perceptions of corruption",
]

metric_cols = st.columns(3)
metric_cols[0].metric("Số bản ghi", f"{len(filtered):,}")
metric_cols[1].metric("Số quốc gia", filtered["Country"].nunique())
metric_cols[2].metric(
    "Điểm trung bình",
    f"{filtered['Happiness Score'].mean():.3f}",
)

tab_explore, tab_compare, tab_factors, tab_data = st.tabs(
    ["🌐 Khám phá", "⚖️ So sánh", "📊 Yếu tố", "📋 Dữ liệu"]
)

with tab_explore:
    chart_col, ranking_col = st.columns([1.5, 1])
    with chart_col:
        selected_factor = st.selectbox(
            "Tô màu theo yếu tố",
            factor_options,
            key="explore_factor",
        )
        fig = px.scatter(
            filtered,
            x="Happiness Score",
            y=selected_factor,
            color="Year",
            hover_name="Country",
            title=f"Điểm hạnh phúc và {selected_factor}",
        )
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

    with ranking_col:
        st.subheader("Top quốc gia")
        st.dataframe(
            filtered.nlargest(10, "Happiness Score")[
                ["Year", "Happiness Rank", "Country", "Happiness Score"]
            ],
            use_container_width=True,
            hide_index=True,
            height=460,
        )

with tab_compare:
    available_countries = sorted(filtered["Country"].dropna().unique())
    default_countries = (
        filtered.nlargest(3, "Happiness Score")["Country"].drop_duplicates().tolist()
    )
    default_countries = [
        country for country in default_countries if country in available_countries
    ]
    selected_countries = st.multiselect(
        "Chọn tối đa 8 quốc gia",
        available_countries,
        default=default_countries,
        max_selections=8,
    )
    if selected_countries:
        comparison = filtered[filtered["Country"].isin(selected_countries)]
        fig = px.line(
            comparison,
            x="Year",
            y="Happiness Score",
            color="Country",
            markers=True,
            title="Thay đổi điểm hạnh phúc theo năm",
        )
        fig.update_layout(height=440)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Chọn ít nhất một quốc gia để xem biểu đồ so sánh.")

with tab_factors:
    factor = st.selectbox("Chọn yếu tố", factor_options, key="factor_analysis")
    factor_data = filtered.dropna(subset=[factor, "Happiness Score"])
    fig = px.scatter(
        factor_data,
        x=factor,
        y="Happiness Score",
        color="Year",
        hover_name="Country",
        title=f"{factor} và điểm hạnh phúc",
    )
    fig.update_layout(height=440)
    st.plotly_chart(fig, use_container_width=True)

    correlation = (
        filtered[["Happiness Score"] + factor_options]
        .corr(numeric_only=True)["Happiness Score"]
        .drop("Happiness Score")
        .sort_values(ascending=False)
        .rename("Hệ số tương quan")
        .to_frame()
    )
    st.dataframe(correlation, use_container_width=True)

with tab_data:
    st.dataframe(
        filtered.sort_values(["Year", "Happiness Rank"]),
        use_container_width=True,
        hide_index=True,
        height=520,
    )
    st.download_button(
        "Tải dữ liệu đã lọc (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="world-happiness-filtered.csv",
        mime="text/csv",
    )