"""Trang phân tích các yếu tố liên quan đến hạnh phúc.

Tính ma trận tương quan, biểu đồ tương quan với điểm hạnh phúc
và pairplot để quan sát mối quan hệ giữa nhiều chỉ số.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_utils import YEARS, apply_theme, load_all_data


st.set_page_config(
    page_title="Yếu tố hạnh phúc",
    page_icon="🔑",
    layout="wide",
)
apply_theme()

st.title("🔑 Các yếu tố liên quan đến hạnh phúc")
st.caption(
    "Khám phá tương quan giữa điểm hạnh phúc và các chỉ số kinh tế - xã hội. "
    "Tương quan không đồng nghĩa với quan hệ nhân quả."
)

data = load_all_data()
if data.empty:
    st.error("Không có dữ liệu để phân tích. Hãy kiểm tra thư mục data.")
    st.stop()

year_options = ["Tất cả năm", *YEARS]
available_regions = sorted(data["Region"].dropna().unique().tolist())
filter_col, region_col = st.columns(2)
with filter_col:
    selected_year = st.selectbox("Năm báo cáo", year_options)
with region_col:
    selected_region = st.selectbox(
        "Khu vực",
        ["Tất cả khu vực", *available_regions],
    )

filtered = data.copy()
if selected_year != "Tất cả năm":
    filtered = filtered.loc[filtered["Year"] == selected_year]
if selected_region != "Tất cả khu vực":
    filtered = filtered.loc[filtered["Region"] == selected_region]

if filtered.empty:
    st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    st.stop()

year_scope = (
    "tất cả các năm" if selected_year == "Tất cả năm" else f"năm {selected_year}"
)
region_scope = (
    "tất cả khu vực"
    if selected_region == "Tất cả khu vực"
    else f"khu vực {selected_region}"
)
filter_scope = f"{year_scope}, {region_scope}"

factor_columns = [
    "Happiness Score",
    "GDP per capita",
    "Social support",
    "Life Expectancy",
    "Freedom",
    "Generosity",
    "Perceptions of corruption",
]
factor_labels = {
    "Happiness Score": "Điểm hạnh phúc",
    "GDP per capita": "GDP bình quân đầu người",
    "Social support": "Hỗ trợ xã hội",
    "Life Expectancy": "Tuổi thọ khỏe mạnh",
    "Freedom": "Tự do lựa chọn",
    "Generosity": "Sự hào phóng",
    "Perceptions of corruption": "Nhận thức về tham nhũng",
}


def describe_correlation(value: float) -> str:
    if abs(value) < 0.2:
        return "yếu, chưa tạo thành xu hướng tuyến tính rõ"
    direction = "cùng chiều" if value > 0 else "ngược chiều"
    if abs(value) >= 0.7:
        strength = "mạnh"
    elif abs(value) >= 0.4:
        strength = "vừa phải"
    else:
        strength = "nhẹ"
    return f"{direction} {strength}"


st.subheader("Ma trận tương quan")
# Loại bỏ cột hoàn toàn rỗng trước khi tính hệ số tương quan Pearson.
corr_data = filtered[factor_columns].dropna(axis=1, how="all")
if len(corr_data.columns) < 2:
    st.info("Không đủ chỉ số có dữ liệu để tính ma trận tương quan.")
else:
    correlation = corr_data.corr(min_periods=2)
    if correlation.dropna(how="all").empty:
        st.info("Không đủ các cặp giá trị hợp lệ để tính tương quan.")
    else:
        correlation_pairs = []
        for left_index, left in enumerate(correlation.columns):
            for right in correlation.columns[left_index + 1 :]:
                value = correlation.loc[left, right]
                if pd.notna(value):
                    correlation_pairs.append(
                        (left, right, float(value))
                    )

        correlation = correlation.rename(
            index=factor_labels,
            columns=factor_labels,
        )
        heatmap = px.imshow(
            correlation,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            aspect="auto",
            labels={"color": "Tương quan"},
            title="Tương quan Pearson giữa các chỉ số",
        )
        heatmap.update_layout(height=620)
        st.plotly_chart(heatmap, use_container_width=True)
        if correlation_pairs:
            clearest_pair = max(
                correlation_pairs, key=lambda pair: abs(pair[2])
            )
            faintest_pair = min(
                correlation_pairs, key=lambda pair: abs(pair[2])
            )
            if any(pair[2] < 0 for pair in correlation_pairs):
                sign_summary = (
                    "Có cả những mối liên hệ cùng chiều lẫn ngược chiều, nên "
                    "các chỉ số không cùng biến động theo một cách duy nhất."
                )
            else:
                sign_summary = (
                    "Các mối liên hệ quan sát được chủ yếu cùng chiều; điều đó "
                    "không có nghĩa mọi chỉ số đều tăng giảm đồng thời ở mọi "
                    "quốc gia."
                )
            st.info(
                "**Nhận xét**\n\n"
                f"Trong {filter_scope}, cặp có mối liên hệ tuyến tính rõ nhất "
                f"là **{factor_labels[clearest_pair[0]]} – "
                f"{factor_labels[clearest_pair[1]]}** "
                f"(liên hệ {describe_correlation(clearest_pair[2])}); cặp "
                f"mờ nhạt nhất là **{factor_labels[faintest_pair[0]]} – "
                f"{factor_labels[faintest_pair[1]]}** "
                f"({describe_correlation(faintest_pair[2])}). {sign_summary} "
                "Các ô màu thể hiện mức độ liên hệ tuyến tính trong dữ liệu, "
                "không cho biết chỉ số nào gây ra thay đổi ở chỉ số khác."
            )
        else:
            st.info(
                "**Nhận xét**\n\n"
                f"Trong {filter_scope}, các chỉ số chưa có đủ biến thiên để "
                "làm nổi bật mối liên hệ tuyến tính giữa từng cặp."
            )

st.subheader("Các chỉ số tương quan với điểm hạnh phúc")
if "Happiness Score" in filtered:
    score_correlations = (
        filtered[factor_columns]
        .corr(min_periods=2)["Happiness Score"]
        .drop("Happiness Score")
        .dropna()
        .rename("Hệ số tương quan Pearson")
        .rename(index=factor_labels)
        .sort_values()
        .rename_axis("Chỉ số")
        .reset_index()
    )
    if score_correlations.empty:
        st.info("Không đủ dữ liệu để tính tương quan với điểm hạnh phúc.")
    else:
        correlation_axis_min = (
            -1
            if score_correlations["Hệ số tương quan Pearson"].min() < 0
            else 0
        )
        correlation_chart = px.bar(
            score_correlations,
            x="Hệ số tương quan Pearson",
            y="Chỉ số",
            color="Hệ số tương quan Pearson",
            color_continuous_scale="RdBu",
            range_color=[-1, 1],
            orientation="h",
            text_auto=".2f",
            title="Tương quan Pearson với điểm hạnh phúc",
        )
        correlation_chart.update_layout(
            height=420,
            xaxis_range=[correlation_axis_min, 1],
            coloraxis_showscale=False,
        )
        st.plotly_chart(correlation_chart, use_container_width=True)
        score_correlation_values = [
            (row["Chỉ số"], float(row["Hệ số tương quan Pearson"]))
            for _, row in score_correlations.iterrows()
        ]
        clearest_score_factor = max(
            score_correlation_values, key=lambda item: abs(item[1])
        )
        faintest_score_factor = min(
            score_correlation_values, key=lambda item: abs(item[1])
        )
        st.info(
            "**Nhận xét**\n\n"
            f"Trong {filter_scope}, **{clearest_score_factor[0]}** là chỉ số "
            f"có mối liên hệ tuyến tính rõ nhất với điểm hạnh phúc "
            f"({describe_correlation(clearest_score_factor[1])}); "
            f"**{faintest_score_factor[0]}** ít thể hiện mối liên hệ tuyến tính "
            f"hơn ({describe_correlation(faintest_score_factor[1])}). Vì vậy, "
            "biểu đồ gợi ý chỉ số nào đáng được chú ý trong phạm vi đang xem, "
            "nhưng không thể kết luận chỉ số đó quyết định mức hạnh phúc hay "
            "có tác động giống nhau ở mọi khu vực."
        )

st.subheader("Pairplot các yếu tố")
# Cho phép người dùng chọn nhiều chỉ số để quan sát ma trận scatter.
selected_factors = st.multiselect(
    "Chọn các chỉ số đưa vào Pairplot (ít nhất 2)",
    options=factor_columns,
    default=[
        "Happiness Score",
        "GDP per capita",
        "Social support",
        "Life Expectancy",
    ],
    format_func=lambda factor: factor_labels[factor],
)

if len(selected_factors) < 2:
    st.info("Hãy chọn ít nhất hai chỉ số để tạo Pairplot.")
else:
    pairplot_data = filtered.dropna(
        subset=selected_factors + ["Country", "Region"]
    )
    if pairplot_data.empty:
        st.warning("Không có đủ bản ghi hoàn chỉnh để tạo Pairplot.")
    else:
        pairplot = px.scatter_matrix(
            pairplot_data,
            dimensions=selected_factors,
            color="Region",
            hover_name="Country",
            opacity=0.65,
            labels=factor_labels,
            title="Phân phối và mối quan hệ giữa các chỉ số",
        )
        pairplot.update_traces(
            diagonal_visible=False,
            showupperhalf=False,
            marker={"size": 6},
        )
        pairplot.update_layout(height=850)
        st.plotly_chart(pairplot, use_container_width=True)
        pairplot_correlations = pairplot_data[selected_factors].corr()
        pairplot_pairs = [
            (
                left,
                right,
                float(pairplot_correlations.loc[left, right]),
            )
            for left_index, left in enumerate(selected_factors)
            for right in selected_factors[left_index + 1 :]
            if pd.notna(pairplot_correlations.loc[left, right])
        ]
        if pairplot_pairs:
            strongest_pair = max(
                pairplot_pairs, key=lambda pair: abs(pair[2])
            )
            if pairplot_data["Region"].nunique() > 1:
                region_observation = (
                    "Màu sắc phân biệt các khu vực, giúp quan sát mức độ tập "
                    "trung và chồng lấp của các nhóm trên từng ô."
                )
            else:
                region_observation = (
                    "Do bộ lọc chỉ còn một khu vực, màu sắc không còn dùng để "
                    "so sánh giữa các khu vực."
                )
            st.info(
                "**Nhận xét**\n\n"
                f"Với các chỉ số đã chọn trong {filter_scope}, cặp có xu hướng "
                f"tuyến tính rõ nhất là **{factor_labels[strongest_pair[0]]} – "
                f"{factor_labels[strongest_pair[1]]}** "
                f"({describe_correlation(strongest_pair[2])}). "
                f"{region_observation} Các điểm vẫn có độ phân tán, nên không "
                "phải quốc gia nào cũng đi theo xu hướng chung; các mối liên "
                "hệ này cũng không chứng minh quan hệ nhân quả. "
                "Khi xem tất cả các năm, một quốc gia có thể xuất hiện ở nhiều "
                "điểm."
            )
        else:
            st.info(
                "**Nhận xét**\n\n"
                f"Pairplot đang dùng các chỉ số đã chọn trong {filter_scope}, "
                "nhưng dữ liệu chưa cho thấy cặp nào có mối liên hệ tuyến tính "
                "đủ rõ để nêu bật. Có thể tiếp tục xem phân bố từng ô và cách "
                "các điểm được nhóm theo khu vực."
            )
