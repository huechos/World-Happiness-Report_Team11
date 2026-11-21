"""Trang theo dõi xu hướng và tương quan các chỉ số hạnh phúc.

Nạp dữ liệu qua nhiều năm, tạo biểu đồ trung bình, biến động điểm hạnh phúc
và phân tán theo các chỉ số được chọn.
"""

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
    """Nạp và chuẩn hóa các file CSV theo năm thành một DataFrame duy nhất."""
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
# Gom dữ liệu theo năm để tính giá trị trung bình của từng chỉ số.
yearly_means = data.groupby("Year", as_index=False)[list(METRIC_LABELS)].mean()
yearly_means_by_year = yearly_means.set_index("Year")
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
trend_insights = []
for metric, label in METRIC_LABELS.items():
    metric_series = yearly_means_by_year[metric].dropna()
    metric_years = metric_series.index.tolist()
    metric_values = metric_series.tolist()
    metric_change = metric_values[-1] - metric_values[0]
    metric_trajectory = " → ".join(
        f"{int(year)}: {value:.3f}"
        for year, value in zip(metric_years, metric_values)
    )
    lowest_year = int(metric_series.idxmin())
    highest_year = int(metric_series.idxmax())
    trend_insights.append(
        f"- **{label}:** {metric_trajectory}. Từ {metric_years[0]} đến "
        f"{metric_years[-1]} chênh lệch ròng {metric_change:+.3f}; "
        f"thấp nhất ở {lowest_year} ({metric_series.min():.3f}), "
        f"cao nhất ở {highest_year} ({metric_series.max():.3f})."
    )
st.info(
    "**Nhận xét chi tiết**\n\n"
    + "\n\n".join(trend_insights)
    + "\n\nMỗi ô biểu đồ dùng một trục tung riêng, vì vậy hãy so sánh xu hướng "
    "trong từng ô; không so sánh trực tiếp độ cao giữa các chỉ số."
)

st.subheader("Biểu đồ vùng điểm hạnh phúc")
# Biểu đồ vùng nhấn mạnh mức thay đổi điểm hạnh phúc trung bình qua từng năm.
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
happiness_area.update_traces(
    mode="lines+markers+text",
    fill="tozeroy",
    fillcolor="rgba(78, 121, 167, 0.16)",
    line={"color": "#315f91", "width": 3},
    marker={"color": "#315f91", "size": 9, "line": {"color": "#ffffff", "width": 2}},
    text=yearly_means["Happiness Score"].map(lambda score: f"{score:.2f}"),
    textposition="top center",
    hovertemplate=(
        "Năm %{x:.0f}<br>"
        "Điểm hạnh phúc trung bình: %{y:.3f}"
        "<extra></extra>"
    ),
)
happiness_area.update_xaxes(
    type="linear",
    tickmode="array",
    tickvals=[int(year) for year in years],
    ticktext=[str(int(year)) for year in years],
    range=[int(years[0]) - 0.25, int(years[-1]) + 0.25],
    title_text="Năm",
    showgrid=False,
)
happiness_area.update_yaxes(
    range=[5, 6],
    dtick=0.1,
    title_text="Điểm hạnh phúc trung bình",
    gridcolor="#e2e8f0",
)
happiness_area.update_layout(
    height=420,
    margin={"t": 70, "b": 45, "l": 45, "r": 25},
    showlegend=False,
)
st.plotly_chart(happiness_area, use_container_width=True)
score_variation = (
    yearly_means_by_year["Happiness Score"].max()
    - yearly_means_by_year["Happiness Score"].min()
)
score_series = yearly_means_by_year["Happiness Score"].dropna()
score_change = score_series.iloc[-1] - score_series.iloc[0]
year_to_year_changes = score_series.diff().dropna()
change_summary = "; ".join(
    f"{int(previous_year)}→{int(year)}: {change:+.3f}"
    for previous_year, year, change in zip(
        score_series.index[:-1],
        year_to_year_changes.index,
        year_to_year_changes,
    )
)
lowest_score_year = int(score_series.idxmin())
highest_score_year = int(score_series.idxmax())
if score_change > 0:
    endpoint_summary = (
        f"tăng {score_change:.3f} điểm, từ {score_series.iloc[0]:.3f} "
        f"({int(score_series.index[0])}) lên {score_series.iloc[-1]:.3f} "
        f"({int(score_series.index[-1])})"
    )
elif score_change < 0:
    endpoint_summary = (
        f"giảm {abs(score_change):.3f} điểm, từ {score_series.iloc[0]:.3f} "
        f"({int(score_series.index[0])}) xuống {score_series.iloc[-1]:.3f} "
        f"({int(score_series.index[-1])})"
    )
else:
    endpoint_summary = (
        f"không đổi, duy trì ở mức {score_series.iloc[0]:.3f} "
        f"qua giai đoạn {int(score_series.index[0])}–"
        f"{int(score_series.index[-1])}"
    )
st.info(
    "**Nhận xét chi tiết**\n\n"
    f"Điểm trung bình {endpoint_summary}. Tuy nhiên, "
    f"mức điểm không tăng đều qua từng năm: {change_summary}. "
    f"Giá trị thấp nhất là {score_series.min():.3f} ({int(lowest_score_year)}), "
    f"cao nhất là {score_series.max():.3f} ({int(highest_score_year)}), với "
    f"biên độ chỉ {score_variation:.3f} điểm. Trục tung 5–6 làm rõ biến động "
    "nhỏ này nên hình dạng có thể khiến chênh lệch trông lớn hơn thực tế; "
    "hãy đối chiếu nhãn số trên từng điểm."
)

st.subheader("Tương quan giữa các chỉ số")
# Cho phép người dùng chọn trục X và năm trước khi vẽ scatter plot.
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
        if correlation > 0:
            correlation_direction = "cùng chiều"
        elif correlation < 0:
            correlation_direction = "ngược chiều"
        else:
            correlation_direction = "không thể hiện xu hướng tuyến tính"
        period_description = (
            "toàn bộ giai đoạn"
            if selected_year == "Tất cả năm"
            else f"năm {selected_year}"
        )
        st.info(
            "**Nhận xét chi tiết**\n\n"
            f"Biểu đồ gồm {len(scatter_data)} điểm trong {period_description}. "
            f"{METRIC_LABELS[x_metric]} trải từ "
            f"{scatter_data[x_metric].min():.3f} đến "
            f"{scatter_data[x_metric].max():.3f}; điểm hạnh phúc trải từ "
            f"{scatter_data['Happiness Score'].min():.3f} đến "
            f"{scatter_data['Happiness Score'].max():.3f}. Hệ số Pearson "
            f"r = {correlation:.3f} cho thấy mối liên hệ tuyến tính "
            f"{correlation_direction}; |r| càng gần 1 thì xu hướng tuyến tính "
            "càng rõ, còn gần 0 thì xu hướng tuyến tính càng yếu. Đây chỉ là "
            "mối liên hệ trong dữ liệu, không chứng minh quan hệ nhân quả. "
            "Khi xem toàn bộ giai đoạn, mỗi điểm là một quan sát quốc gia-năm, "
            "nên một quốc gia có thể xuất hiện ở nhiều năm."
        )
