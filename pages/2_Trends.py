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
st.info(
    "**Nhận xét**\n\n"
    "Quan sát ba đường xu hướng cạnh nhau cho thấy điểm hạnh phúc khá ổn định "
    "so với những nhịp lên xuống rõ hơn ở GDP và tuổi thọ. GDP tăng trong "
    "những năm đầu rồi chững lại, còn tuổi thọ giảm trước khi phục hồi về cuối "
    "giai đoạn. Diễn biến này gợi ý rằng chất lượng cuộc sống không chỉ gắn "
    "với kinh tế hay sức khỏe; các yếu tố xã hội và cảm nhận cá nhân cũng "
    "đáng được xem xét. Đây là nhận định từ xu hướng quan sát được, không "
    "phải kết luận rằng chỉ số nào gây ra hạnh phúc. Mỗi ô có trục tung riêng "
    "nên cần so sánh hình dạng xu hướng trong từng ô."
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
st.info(
    "**Nhận xét**\n\n"
    "Thoạt nhìn, đường điểm hạnh phúc gần như đi ngang và không có bước ngoặt "
    "lớn trong giai đoạn này. Có một nhịp chùng xuống rồi mới nhích "
    "lên, nên cảm giác chung là sự cải thiện khá từ tốn chứ không tăng đều "
    "qua từng năm. Trục tung được thu hẹp còn 5–6 để nhìn rõ những dao động "
    "nhỏ, vì vậy độ dốc trên hình có thể trông mạnh hơn thực tế. Cần đối chiếu "
    "các nhãn số trước khi kết luận mức thay đổi là đáng kể."
)

st.subheader("Tương quan giữa các chỉ số")
# Cho phép người dùng chọn trục X và năm trước khi vẽ scatter plot.
control_col, year_col = st.columns(2)
with control_col:
    scatter_metrics = [
        metric for metric in METRIC_LABELS if metric != "Happiness Score"
    ]
    x_metric = st.selectbox(
        "Chỉ số trên trục X",
        options=scatter_metrics,
        index=scatter_metrics.index("GDP per capita"),
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
        if abs(correlation) >= 0.7:
            correlation_strength = "khá rõ"
        elif abs(correlation) >= 0.4:
            correlation_strength = "vừa phải"
        elif abs(correlation) >= 0.2:
            correlation_strength = "khá nhẹ"
        else:
            correlation_strength = "khó nhận ra"
        yearly_correlations = {}
        for year, year_data in data.groupby("Year"):
                paired_values = year_data[[x_metric, "Happiness Score"]].dropna()
                if len(paired_values) >= 2:
                    yearly_correlations[int(year)] = paired_values[x_metric].corr(
                        paired_values["Happiness Score"]
                    )
        yearly_correlations = pd.Series(yearly_correlations).dropna()

        if correlation > 0:
            relationship_description = (
                    f"các quốc gia có {METRIC_LABELS[x_metric]} cao hơn thường "
                    "cũng có điểm hạnh phúc cao hơn"
            )
        elif correlation < 0:
            relationship_description = (
                    f"các quốc gia có {METRIC_LABELS[x_metric]} cao hơn có xu "
                    "hướng có điểm hạnh phúc thấp hơn"
            )
        else:
            relationship_description = (
                    f"đám mây điểm chưa cho thấy {METRIC_LABELS[x_metric]} đi "
                    "cùng một xu hướng tăng hoặc giảm rõ rệt của điểm hạnh phúc"
            )
        if selected_year == "Tất cả năm":
                if yearly_correlations.empty:
                    year_comparison = (
                        "Chưa đủ dữ liệu theo từng năm để so sánh sự ổn định của "
                        "mối liên hệ này."
                    )
                else:
                    strongest_year = int(yearly_correlations.abs().idxmax())
                    weakest_year = int(yearly_correlations.abs().idxmin())
                    signs = set(
                        yearly_correlations.apply(
                            lambda value: 1 if value > 0 else -1 if value < 0 else 0
                        )
                    )
                    nonzero_signs = signs - {0}
                    if len(nonzero_signs) <= 1:
                        consistency = (
                            "Chiều liên hệ nhìn chung được giữ nguyên qua các năm, "
                            "nên xu hướng chung không chỉ đến từ một năm riêng lẻ."
                        )
                    else:
                        consistency = (
                            "Chiều liên hệ có lúc đảo ngược giữa các năm; vì vậy "
                            "kết quả gộp cần được diễn giải thận trọng."
                        )
                    year_comparison = (
                        f"{consistency} Xu hướng rõ nhất xuất hiện ở {strongest_year}, "
                        f"còn mờ nhất ở {weakest_year}."
                    )
                period_description = "toàn bộ giai đoạn"
                repeated_country_note = (
                    " Một quốc gia có thể xuất hiện nhiều lần do dữ liệu gồm nhiều "
                    "năm."
                )
        else:
                selected_year_value = int(selected_year)
                if selected_year_value in yearly_correlations.index:
                    selected_strength = abs(
                        yearly_correlations.loc[selected_year_value]
                    )
                    strongest_strength = yearly_correlations.abs().max()
                    weakest_strength = yearly_correlations.abs().min()
                    if selected_strength == strongest_strength:
                        year_comparison = (
                            "Trong các năm báo cáo, đây là một trong những năm có "
                            "mối liên hệ rõ nhất."
                        )
                    elif selected_strength == weakest_strength:
                        year_comparison = (
                            "So với các năm còn lại, mối liên hệ trong năm này thuộc "
                            "nhóm mờ nhạt nhất."
                        )
                    else:
                        year_comparison = (
                            "Mức độ liên hệ trong năm này nằm giữa mức mạnh nhất và "
                            "yếu nhất của các năm báo cáo."
                        )
                    pooled_values = data[[x_metric, "Happiness Score"]].dropna()
                    pooled_correlation = pooled_values[x_metric].corr(
                        pooled_values["Happiness Score"]
                    )
                    if correlation * pooled_correlation < 0:
                        year_comparison += (
                            " Hướng của mối liên hệ cũng khác với xu hướng khi gộp "
                            "toàn bộ các năm."
                        )
                    elif abs(correlation - pooled_correlation) <= 0.05:
                        year_comparison += (
                            " Hướng và mức độ nhìn chung gần với xu hướng của toàn "
                            "giai đoạn."
                        )
                    elif abs(correlation) > abs(pooled_correlation):
                        year_comparison += (
                            " Mối liên hệ trong năm này rõ hơn xu hướng khi gộp "
                            "toàn bộ các năm."
                        )
                    else:
                        year_comparison += (
                            " Mối liên hệ trong năm này yếu hơn xu hướng khi gộp "
                            "toàn bộ các năm."
                        )
                else:
                    year_comparison = (
                        "Chưa đủ dữ liệu ở năm này để đối chiếu với các năm khác."
                    )
                period_description = f"năm {selected_year}"
                repeated_country_note = ""

        st.info(
                "**Nhận xét**\n\n"
                f"Với {METRIC_LABELS[x_metric]}, trong {period_description}, "
                f"{relationship_description}. Mẫu hình này {correlation_strength}. "
                f"{year_comparison} Những điểm nằm xa xu hướng chung cho thấy vẫn "
                "có các quốc gia khác biệt, nên chỉ số này không thể giải thích "
                "riêng lẻ mức hạnh phúc. Tương quan cũng không chứng minh quan hệ "
                f"nhân quả.{repeated_country_note}"
        )
