from pathlib import Path
import re

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
METRIC_LABELS = {
    "Happiness Score": "Điểm hạnh phúc",
    "GDP per capita": "GDP bình quân đầu người",
    "Life Expectancy": "Tuổi thọ khỏe mạnh",
}
COLUMN_ALIASES = {
    "country": "Country",
    "countryorregion": "Country",
    "score": "Happiness Score",
    "happinessscore": "Happiness Score",
    "economygdppercapita": "GDP per capita",
    "gdppercapita": "GDP per capita",
    "healthlifeexpectancy": "Life Expectancy",
    "lifeexpectancy": "Life Expectancy",
}

st.title("📈 Xu hướng & tương quan")
st.markdown(
    "Theo dõi biến động các chỉ số qua từng năm và khám phá mối liên hệ "
    "giữa GDP, tuổi thọ khỏe mạnh và điểm hạnh phúc."
)


@st.cache_data
def load_all_years(data_dir: str) -> pd.DataFrame:
    data_path = Path(data_dir)
    year_files = sorted(
        (
            (int(path.stem), path)
            for path in data_path.glob("*.csv")
            if path.stem.isdigit()
        ),
        key=lambda item: item[0],
    )
    if not year_files:
        raise FileNotFoundError(f"Không tìm thấy file CSV theo năm trong {data_path}")

    frames = []
    for year, path in year_files:
        frame = pd.read_csv(path)
        column_mapping = {}
        for column in frame.columns:
            normalized = re.sub(r"[^a-z0-9]", "", str(column).lower())
            canonical = COLUMN_ALIASES.get(normalized)
            if canonical and canonical not in frame.columns:
                column_mapping[column] = canonical
        frame = frame.rename(columns=column_mapping)

        required_columns = ["Country", *METRIC_LABELS]
        missing_columns = [column for column in required_columns if column not in frame.columns]
        if missing_columns:
            raise ValueError(
                f"{path.name} thiếu các cột cần thiết: {', '.join(missing_columns)}"
            )

        frame["Year"] = year
        for metric in METRIC_LABELS:
            frame[metric] = pd.to_numeric(frame[metric], errors="coerce")
        frames.append(frame[["Year", "Country", *METRIC_LABELS]])

    return pd.concat(frames, ignore_index=True)


try:
    data = load_all_years(str(DATA_DIR))
except (FileNotFoundError, pd.errors.ParserError, ValueError) as error:
    st.error(f"Không thể tải dữ liệu xu hướng: {error}")
    st.stop()

years = sorted(data["Year"].dropna().unique().tolist())
if not years:
    st.warning("Không có dữ liệu năm hợp lệ để hiển thị.")
    st.stop()

st.subheader("Xu hướng trung bình theo năm")
yearly_means = data.groupby("Year", as_index=False)[list(METRIC_LABELS)].mean()
trend_data = yearly_means.melt(
    id_vars="Year",
    value_vars=list(METRIC_LABELS),
    var_name="Metric",
    value_name="Average",
)
trend_data["Chỉ số"] = trend_data["Metric"].map(METRIC_LABELS)

trend_figure = px.line(
    trend_data,
    x="Year",
    y="Average",
    color="Chỉ số",
    facet_col="Chỉ số",
    facet_col_wrap=3,
    category_orders={"Chỉ số": list(METRIC_LABELS.values())},
    markers=True,
    labels={"Year": "Năm", "Average": "Giá trị trung bình"},
    title="Điểm hạnh phúc, GDP và tuổi thọ khỏe mạnh",
)
trend_figure.update_yaxes(matches=None, showticklabels=True)
trend_figure.update_xaxes(dtick=1)
trend_figure.update_layout(
    height=420,
    showlegend=False,
    margin={"t": 85, "b": 35, "l": 35, "r": 20},
)
trend_figure.for_each_annotation(
    lambda annotation: annotation.update(text=annotation.text.split("=")[-1])
)
st.plotly_chart(trend_figure, use_container_width=True)

st.subheader("Biểu đồ vùng điểm hạnh phúc")
happiness_area = px.area(
    yearly_means,
    x="Year",
    y="Happiness Score",
    labels={
        "Year": "Năm",
        "Happiness Score": "Điểm hạnh phúc trung bình",
    },
    title="Điểm hạnh phúc trung bình qua các năm",
    color_discrete_sequence=["#4E79A7"],
)
happiness_area.update_xaxes(dtick=1)
happiness_area.update_layout(height=360, margin={"t": 70, "b": 35, "l": 35, "r": 20})
st.plotly_chart(happiness_area, use_container_width=True)

first_year, latest_year = years[0], years[-1]
first_averages = yearly_means.set_index("Year").loc[first_year]
latest_averages = yearly_means.set_index("Year").loc[latest_year]
score_change = latest_averages["Happiness Score"] - first_averages["Happiness Score"]
score_direction = "tăng" if score_change >= 0 else "giảm"
st.info(
    f"Gợi ý cho Phần 3 báo cáo: từ {first_year} đến {latest_year}, "
    f"điểm hạnh phúc trung bình {score_direction} "
    f"{abs(score_change):.3f} điểm "
    f"({first_averages['Happiness Score']:.3f} → "
    f"{latest_averages['Happiness Score']:.3f}). "
    "Các đường GDP và tuổi thọ dùng trục tung riêng để dễ so sánh xu hướng."
)

st.subheader("Tương quan giữa các chỉ số")
control_col, year_col = st.columns(2)
with control_col:
    x_metric = st.selectbox(
        "Chỉ số trên trục X",
        options=list(METRIC_LABELS),
        index=list(METRIC_LABELS).index("GDP per capita"),
        format_func=lambda metric: METRIC_LABELS[metric],
    )
with year_col:
    year_options = ["Tất cả năm", *years]
    selected_year = st.selectbox("Lọc theo năm", options=year_options)

scatter_data = data
if selected_year != "Tất cả năm":
    scatter_data = scatter_data[scatter_data["Year"] == selected_year]
scatter_data = scatter_data.dropna(subset=[x_metric, "Happiness Score"])

if scatter_data.empty:
    st.warning("Không có đủ dữ liệu để vẽ biểu đồ tương quan với lựa chọn hiện tại.")
else:
    scatter_figure = px.scatter(
        scatter_data,
        x=x_metric,
        y="Happiness Score",
        color="Year",
        hover_name="Country",
        hover_data={"Year": True},
        labels={
            x_metric: METRIC_LABELS[x_metric],
            "Happiness Score": METRIC_LABELS["Happiness Score"],
            "Year": "Năm",
        },
        title=(
            f"{METRIC_LABELS[x_metric]} và "
            f"{METRIC_LABELS['Happiness Score']}"
        ),
        opacity=0.75,
    )
    scatter_figure.update_layout(height=520)
    st.plotly_chart(scatter_figure, use_container_width=True)

    correlation = scatter_data[x_metric].corr(scatter_data["Happiness Score"])
    if pd.isna(correlation):
        st.caption("Không thể tính hệ số tương quan từ các giá trị hiện có.")
    else:
        st.metric("Hệ số tương quan Pearson", f"{correlation:.3f}")
        st.caption(
            "Hệ số thể hiện mức độ liên hệ tuyến tính trong dữ liệu được lọc; "
            "tương quan không đồng nghĩa với quan hệ nhân quả."
        )
