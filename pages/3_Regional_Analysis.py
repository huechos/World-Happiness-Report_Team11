"""Trang phân tích so sánh giữa các khu vực.

Hỗ trợ lọc theo năm và khu vực, tương tác địa cầu, biểu đồ tổng hợp
và so sánh điểm hạnh phúc của nhiều quốc gia.
"""

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
# Áp dụng bộ lọc năm và danh sách khu vực theo lựa chọn của người dùng.
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
# Tổng hợp điểm trung bình và số quốc gia duy nhất cho mỗi khu vực.
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
        color_discrete_map=REGION_COLORS,
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
    if len(region_summary) == 1:
        score_comment = (
            f"Với bộ lọc hiện tại, chỉ còn {region_summary.iloc[0]['Region']} "
            "nên biểu đồ cho thấy mức điểm của khu vực này, chưa thể so sánh "
            "với các khu vực khác."
        )
    else:
        highest_score_region = region_summary.iloc[0]
        lowest_score_region = region_summary.iloc[-1]
        score_period = (
            "giai đoạn được chọn"
            if selected_year == "Tất cả năm"
            else f"năm {selected_year}"
        )
        score_comment = (
            f"Trong {score_period}, "
            f"{highest_score_region['Region']} đang có điểm trung bình cao nhất, "
            f"còn {lowest_score_region['Region']} thấp nhất. Chênh lệch giữa "
            "các mức trung bình cho thấy trải nghiệm hạnh phúc có thể khác "
            "nhau theo khu vực; tuy nhiên, điểm trung bình không đại diện cho "
            "mọi quốc gia hay mọi người dân trong khu vực."
        )
    st.info(f"**Nhận xét**\n\n{score_comment}")

st.subheader("Số quốc gia theo khu vực")
count_chart = px.bar(
    region_summary.sort_values("Số quốc gia"),
    x="Số quốc gia",
    y="Region",
    color="Region",
    color_discrete_map=REGION_COLORS,
    orientation="h",
    text="Số quốc gia",
    labels={"Region": "Khu vực"},
    title="Số quốc gia có dữ liệu trong lựa chọn hiện tại",
)
count_chart.update_layout(height=460, showlegend=False, yaxis_title="")
st.plotly_chart(count_chart, use_container_width=True)
if len(region_summary) == 1:
    count_comment = (
        f"Bộ lọc hiện tại chỉ có dữ liệu cho {region_summary.iloc[0]['Region']}; "
        "vì vậy chưa thể nhận xét khu vực nào có độ phủ quốc gia lớn hơn."
    )
else:
    most_countries = region_summary.loc[region_summary["Số quốc gia"].idxmax()]
    fewest_countries = region_summary.loc[region_summary["Số quốc gia"].idxmin()]
    count_period = (
        "toàn bộ giai đoạn"
        if selected_year == "Tất cả năm"
        else f"năm {selected_year}"
    )
    count_comment = (
        f"Trong {count_period}, {most_countries['Region']} có độ phủ quốc gia "
        f"lớn nhất trong dữ liệu, còn {fewest_countries['Region']} ít nhất. "
        "Đây là số quốc gia được ghi nhận, không phải quy mô dân số hay mức "
        "hạnh phúc; khu vực có nhiều quốc gia hơn không mặc nhiên hạnh phúc hơn."
    )
st.info(f"**Nhận xét**\n\n{count_comment}")

st.subheader("So sánh nhiều quốc gia")
# Cho phép chọn ít nhất hai quốc gia để vẽ đường thay đổi theo thời gian.
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
        country_summaries = []
        for country, country_data in comparison_data.groupby("Country"):
            country_data = country_data.sort_values("Year")
            if len(country_data) >= 2:
                country_summaries.append(
                    {
                        "Country": country,
                        "Start": country_data.iloc[0]["Happiness Score"],
                        "End": country_data.iloc[-1]["Happiness Score"],
                        "Change": (
                            country_data.iloc[-1]["Happiness Score"]
                            - country_data.iloc[0]["Happiness Score"]
                        ),
                    }
                )
        latest_country_scores = (
            comparison_data.sort_values("Year")
            .groupby("Country", as_index=False)
            .tail(1)
            .sort_values("Happiness Score", ascending=False)
        )
        if country_summaries:
            greatest_rise = max(
                country_summaries, key=lambda summary: summary["Change"]
            )
            greatest_fall = min(
                country_summaries, key=lambda summary: summary["Change"]
            )
            if greatest_rise["Change"] > 0:
                change_comment = (
                    f"{greatest_rise['Country']} có mức cải thiện rõ nhất trong "
                    "nhóm được chọn"
                )
            else:
                change_comment = (
                    "không quốc gia nào trong nhóm có mức tăng qua các mốc "
                    "được ghi nhận"
                )
            if greatest_fall["Change"] < 0:
                change_comment += (
                    f", trong khi {greatest_fall['Country']} giảm nhiều nhất"
                )
            else:
                change_comment += (
                    "; các quốc gia trong nhóm đều giữ mức điểm ổn định hoặc "
                    "tăng lên"
                )
            comparison_comment = (
                f"Ở lần ghi nhận gần nhất, {latest_country_scores.iloc[0]['Country']} "
                f"đang có điểm cao nhất trong nhóm. Nhìn theo thời gian, "
                f"{change_comment}. Các đường đi khác nhau nhắc rằng xu hướng "
                "chung không nhất thiết phản ánh trải nghiệm của từng quốc gia."
            )
        else:
            comparison_comment = (
                "Chưa đủ dữ liệu ở nhiều năm cho các quốc gia đã chọn để nhận "
                "xét xu hướng tăng giảm; biểu đồ hiện chủ yếu giúp so sánh "
                "các lần ghi nhận đang có."
            )
        st.info(f"**Nhận xét**\n\n{comparison_comment}")
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
    region_changes = []
    for region, region_data in trend_data.groupby("Region"):
        region_data = region_data.sort_values("Year")
        if len(region_data) >= 2:
            region_changes.append(
                {
                    "Region": region,
                    "Change": (
                        region_data.iloc[-1]["Happiness Score"]
                        - region_data.iloc[0]["Happiness Score"]
                    ),
                    "Range": (
                        region_data["Happiness Score"].max()
                        - region_data["Happiness Score"].min()
                    ),
                }
            )
    if region_changes:
        largest_rise = max(region_changes, key=lambda item: item["Change"])
        smallest_rise = min(region_changes, key=lambda item: item["Change"])
        most_steady = min(region_changes, key=lambda item: item["Range"])
        if largest_rise["Change"] > 0:
            trend_comment = (
                f"{largest_rise['Region']} có xu hướng cải thiện rõ nhất trong "
                "các khu vực"
            )
        else:
            trend_comment = (
                "các khu vực nhìn chung không cho thấy mức tăng rõ rệt giữa "
                "đầu và cuối giai đoạn"
            )
        if smallest_rise["Change"] < 0:
            trend_comment += (
                f", còn {smallest_rise['Region']} là khu vực giảm nhiều nhất"
            )
        else:
            trend_comment += (
                f"; {most_steady['Region']} có đường xu hướng ổn định nhất"
            )
        trend_comment += (
            ". Các đường không biến động đồng đều, cho thấy mỗi khu vực có "
            "nhịp thay đổi riêng; mức trung bình khu vực cũng có thể che khuất "
            "khác biệt giữa các quốc gia."
        )
    else:
        trend_comment = (
            "Chưa có đủ các mốc năm để so sánh diễn biến của từng khu vực."
        )
    trend_period = (
        f"từ {int(trend_data['Year'].min())} đến {int(trend_data['Year'].max())}"
    )
    trend_comment = f"Trong giai đoạn {trend_period}, {trend_comment}"
    st.info(f"**Nhận xét**\n\n{trend_comment}")

st.subheader("Dữ liệu theo khu vực")
st.dataframe(
    filtered.sort_values(["Year", "Happiness Rank"], na_position="last"),
    use_container_width=True,
    hide_index=True,
)
