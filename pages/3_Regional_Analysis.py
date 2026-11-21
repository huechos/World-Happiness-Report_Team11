import json

import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import streamlit as st

from dashboard_utils import YEARS, apply_theme, load_all_data
from globe_component import render_globe_component


REGION_COLORS = {
    "Western Europe": "#4E79A7",
    "North America": "#F28E2B",
    "Australia and New Zealand": "#E15759",
    "Middle East and Northern Africa": "#76B7B2",
    "Latin America and Caribbean": "#59A14F",
    "Southeastern Asia": "#EDC948",
    "Central and Eastern Europe": "#B07AA1",
    "Eastern Asia": "#FF9DA7",
    "Sub-Saharan Africa": "#9C755F",
    "Southern Asia": "#BAB0AC",
}


st.set_page_config(
    page_title="Phân tích khu vực",
    page_icon="🌎",
    layout="wide",
)
apply_theme()

st.title("🌎 Phân tích khu vực")
st.caption(
    "So sánh điểm hạnh phúc và số lượng quốc gia giữa các khu vực "
    "qua các năm báo cáo."
)

data = load_all_data()
if data.empty:
    st.error("Không có dữ liệu để phân tích. Hãy kiểm tra thư mục data.")
    st.stop()

year_options = ["Tất cả năm", *YEARS]
filter_col, region_col = st.columns(2)
with filter_col:
    selected_year = st.selectbox("Năm báo cáo", year_options)
with region_col:
    available_regions = sorted(data["Region"].dropna().unique().tolist())
    if "regional_region_filter" not in st.session_state:
        st.session_state["regional_region_filter"] = []
    if "regional_pending_regions" in st.session_state:
        pending_regions = st.session_state["regional_pending_regions"]
        del st.session_state["regional_pending_regions"]
        st.session_state["regional_region_filter"] = [
            region for region in pending_regions if region in available_regions
        ]
    current_regions = st.session_state["regional_region_filter"]
    if isinstance(current_regions, str):
        current_regions = [current_regions] if current_regions in available_regions else []
    if not isinstance(current_regions, (list, tuple)):
        current_regions = []
    st.session_state["regional_region_filter"] = [
        region for region in current_regions if region in available_regions
    ]
    selected_regions = st.multiselect(
        "Khu vực (có thể chọn nhiều)",
        available_regions,
        key="regional_region_filter",
    )

filtered = data.copy()
if selected_year != "Tất cả năm":
    filtered = filtered.loc[filtered["Year"] == selected_year]
if selected_regions:
    filtered = filtered.loc[filtered["Region"].isin(selected_regions)]

if filtered.empty:
    st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    st.stop()

st.subheader("Chọn khu vực trên quả địa cầu")
st.caption(
    "Bấm vào một quốc gia để chọn/bỏ chọn khu vực của quốc gia đó. "
    "Có thể chọn nhiều khu vực; bỏ trống bộ lọc để xem tất cả. "
    "Khi chọn tất cả các năm, quả địa cầu hiển thị dữ liệu năm mới nhất."
)
map_year = (
    int(selected_year)
    if selected_year != "Tất cả năm"
    else int(data["Year"].max())
)
map_data = data.loc[data["Year"] == map_year].dropna(
    subset=["Country", "Region"]
)
globe = px.choropleth(
    map_data,
    locations="Country",
    locationmode="country names",
    color="Region",
    hover_name="Country",
    hover_data={"Region": True},
    custom_data=["Region"],
    color_discrete_map=REGION_COLORS,
    projection="orthographic",
)
globe.update_traces(marker_line_color="#f8fafc", marker_line_width=0.6)
if selected_regions:
    for trace in globe.data:
        trace.selectedpoints = (
            list(range(len(trace.locations)))
            if trace.name in selected_regions
            else []
        )
        trace.selected = {"marker": {"opacity": 1}}
        trace.unselected = {"marker": {"opacity": 0.15}}
globe.update_geos(
    showland=True,
    landcolor="#e8eef4",
    showcountries=True,
    countrycolor="#94a3b8",
    showocean=True,
    oceancolor="#dbeafe",
)
globe.update_layout(
    height=520,
    margin={"l": 0, "r": 0, "t": 10, "b": 0},
    legend_title_text="Khu vực",
    uirevision="regional-globe",
)
globe_selection = render_globe_component(
    figure_json=json.dumps(globe.to_dict(), cls=PlotlyJSONEncoder),
    height=520,
    key="regional-globe",
    selected_regions=selected_regions,
    selection_mode="multiple",
)
if isinstance(globe_selection, dict):
    event_id = globe_selection.get("event_id")
    if event_id and event_id != st.session_state.get("regional_last_globe_event"):
        st.session_state["regional_last_globe_event"] = event_id
        clicked_regions = globe_selection.get("regions")
        if isinstance(clicked_regions, list):
            clicked_regions = [
                region for region in clicked_regions if region in available_regions
            ]
        else:
            clicked_region = globe_selection.get("region")
            clicked_regions = (
                [clicked_region]
                if clicked_region in available_regions
                else selected_regions
            )
        if set(clicked_regions) != set(selected_regions):
            st.session_state["regional_pending_regions"] = clicked_regions
            st.rerun()

scored = filtered.dropna(subset=["Region", "Happiness Score"])
region_summary = (
    scored.groupby("Region", as_index=False)
    .agg(
        **{
            "Điểm hạnh phúc trung bình": ("Happiness Score", "mean"),
            "Số quốc gia": ("Country", "nunique"),
        }
    )
    .sort_values("Điểm hạnh phúc trung bình", ascending=False)
)

top_region = (
    region_summary.iloc[0]["Region"] if not region_summary.empty else "—"
)
metric_cols = st.columns(3)
metric_cols[0].metric("Số khu vực", f"{filtered['Region'].nunique():,}")
metric_cols[1].metric("Số quốc gia", f"{filtered['Country'].nunique():,}")
metric_cols[2].metric("Điểm trung bình cao nhất", top_region)

st.subheader("Điểm hạnh phúc trung bình theo khu vực")
if region_summary.empty:
    st.info("Không có điểm hạnh phúc hợp lệ để so sánh.")
else:
    score_chart = px.bar(
        region_summary.sort_values("Điểm hạnh phúc trung bình"),
        x="Điểm hạnh phúc trung bình",
        y="Region",
        color="Region",
        orientation="h",
        text_auto=".2f",
        labels={"Region": "Khu vực"},
        title="Điểm hạnh phúc trung bình",
    )
    score_chart.update_layout(
        height=460,
        showlegend=False,
        xaxis_title="Điểm hạnh phúc trung bình",
        yaxis_title="",
    )
    st.plotly_chart(score_chart, use_container_width=True)

st.subheader("Số quốc gia theo khu vực")
count_chart = px.bar(
    region_summary.sort_values("Số quốc gia"),
    x="Số quốc gia",
    y="Region",
    color="Region",
    orientation="h",
    text="Số quốc gia",
    labels={"Region": "Khu vực"},
    title="Số quốc gia có dữ liệu trong lựa chọn hiện tại",
)
count_chart.update_layout(height=460, showlegend=False, yaxis_title="")
st.plotly_chart(count_chart, use_container_width=True)

st.subheader("So sánh nhiều quốc gia")
available_countries = sorted(data["Country"].dropna().unique().tolist())
selected_countries = st.multiselect(
    "Chọn các quốc gia muốn so sánh",
    options=available_countries,
    help="Có thể chọn nhiều quốc gia; biểu đồ so sánh điểm hạnh phúc qua các năm.",
    key="regional_country_comparison",
)
if len(selected_countries) >= 2:
    comparison_data = data.loc[
        data["Country"].isin(selected_countries)
    ].dropna(subset=["Happiness Score"])
    if comparison_data.empty:
        st.warning("Các quốc gia đã chọn không có điểm hạnh phúc để so sánh.")
    else:
        comparison_chart = px.line(
            comparison_data,
            x="Year",
            y="Happiness Score",
            color="Country",
            markers=True,
            hover_data={"Region": True, "Happiness Rank": True},
            labels={
                "Year": "Năm",
                "Happiness Score": "Điểm hạnh phúc",
                "Country": "Quốc gia",
            },
            title="Điểm hạnh phúc của các quốc gia qua các năm",
        )
        comparison_chart.update_xaxes(dtick=1)
        comparison_chart.update_layout(height=480)
        st.plotly_chart(comparison_chart, use_container_width=True)
        st.dataframe(
            comparison_data.sort_values(["Country", "Year"])[
                ["Year", "Country", "Region", "Happiness Rank", "Happiness Score"]
            ],
            use_container_width=True,
            hide_index=True,
        )
else:
    st.info("Chọn ít nhất hai quốc gia để so sánh xu hướng.")

if selected_year == "Tất cả năm" and not selected_regions:
    st.subheader("Xu hướng điểm hạnh phúc theo khu vực")
    trend_data = (
        data.dropna(subset=["Region", "Happiness Score"])
        .groupby(["Year", "Region"], as_index=False)["Happiness Score"]
        .mean()
    )
    trend_chart = px.line(
        trend_data,
        x="Year",
        y="Happiness Score",
        color="Region",
        markers=True,
        labels={
            "Year": "Năm",
            "Happiness Score": "Điểm hạnh phúc trung bình",
            "Region": "Khu vực",
        },
        title="Điểm hạnh phúc trung bình theo khu vực qua các năm",
    )
    trend_chart.update_xaxes(dtick=1)
    trend_chart.update_layout(height=480)
    st.plotly_chart(trend_chart, use_container_width=True)

st.subheader("Dữ liệu theo khu vực")
st.dataframe(
    filtered.sort_values(["Year", "Happiness Rank"], na_position="last"),
    use_container_width=True,
    hide_index=True,
)
