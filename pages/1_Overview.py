import json
from pathlib import Path

import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import streamlit as st
from globe_component import render_globe_component


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
YEARS = [2015, 2016, 2017, 2018, 2019]
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


def load_data_by_year(year):
    return pd.read_csv(DATA_DIR / f"{year}.csv")


def clear_region_selection():
    st.session_state["overview_selected_region"] = None
    st.session_state["overview_globe_generation"] += 1


st.title("📊 Phân tích theo từng năm độc lập")
selected_year = st.selectbox("Chọn năm báo cáo:", YEARS)
df = load_data_by_year(selected_year)

if "overview_selected_region" not in st.session_state:
    st.session_state["overview_selected_region"] = None
if "overview_globe_generation" not in st.session_state:
    st.session_state["overview_globe_generation"] = 0

regions = set(df["Region"].dropna())
selected_region = st.session_state["overview_selected_region"]
if selected_region not in regions:
    selected_region = None
    st.session_state["overview_selected_region"] = None

st.subheader("Chọn khu vực trên quả địa cầu")
st.caption(
    "Kéo ngang hoặc dọc để xoay quả địa cầu. "
    "Bấm vào một quốc gia để xem danh sách các quốc gia cùng khu vực."
)

map_data = df.dropna(subset=["Country", "Region"])
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
if selected_region:
    for trace in globe.data:
        trace.selectedpoints = (
            list(range(len(trace.locations))) if trace.name == selected_region else []
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
    projection_rotation={"lat": 0, "lon": 0, "roll": 0},
)
globe.update_layout(
    height=520,
    margin={"l": 0, "r": 0, "t": 10, "b": 0},
    legend_title_text="Khu vực",
    uirevision="overview-globe",
)

globe_selection = render_globe_component(
    figure_json=json.dumps(globe.to_dict(), cls=PlotlyJSONEncoder),
    height=520,
    key=(
        f"overview_globe_{selected_year}_"
        f"{st.session_state['overview_globe_generation']}"
    ),
)
if isinstance(globe_selection, dict):
    clicked_region = globe_selection.get("region")
    if clicked_region in regions and clicked_region != selected_region:
        st.session_state["overview_selected_region"] = clicked_region
        st.rerun()

selected_region = st.session_state["overview_selected_region"]
if selected_region not in regions:
    selected_region = None
    st.session_state["overview_selected_region"] = None

if selected_region:
    st.write(f"Đang chọn khu vực **{selected_region}** trong năm **{selected_year}**.")
    st.button("Bỏ chọn khu vực", on_click=clear_region_selection)
    visible_data = df.loc[df["Region"] == selected_region]
else:
    st.write(
        f"Đang hiển thị toàn bộ dữ liệu năm **{selected_year}** "
        f"(Tổng số quốc gia: {len(df)})"
    )
    visible_data = df

st.dataframe(visible_data, use_container_width=True)
