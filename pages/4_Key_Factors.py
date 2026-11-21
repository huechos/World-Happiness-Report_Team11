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
                    pair_count = corr_data[[left, right]].dropna().shape[0]
                    correlation_pairs.append(
                        (left, right, float(value), pair_count)
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
            highest_pair = max(correlation_pairs, key=lambda pair: pair[2])
            lowest_pair = min(correlation_pairs, key=lambda pair: pair[2])
            st.info(
                "**Nhận xét chi tiết**\n\n"
                f"Ma trận đang phản ánh {len(filtered)} bản ghi trong "
                f"{filter_scope}. Cặp có hệ số cao nhất là "
                f"**{factor_labels[highest_pair[0]]} – "
                f"{factor_labels[highest_pair[1]]}** "
                f"(r = {highest_pair[2]:.3f}, n = {highest_pair[3]}); "
                f"cặp có hệ số thấp nhất là **{factor_labels[lowest_pair[0]]} – "
                f"{factor_labels[lowest_pair[1]]}** "
                f"(r = {lowest_pair[2]:.3f}, n = {lowest_pair[3]}). "
                "Hệ số dương biểu thị xu hướng cùng chiều, hệ số âm là ngược "
                "chiều; |r| càng gần 1 thì liên hệ tuyến tính càng rõ, còn gần "
                "0 thì liên hệ tuyến tính càng yếu. Đường chéo bằng 1 vì mỗi "
                "chỉ số được so sánh với chính nó."
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
        highest_score_correlation = score_correlations.iloc[-1]
        lowest_score_correlation = score_correlations.iloc[0]
        st.info(
            "**Nhận xét chi tiết**\n\n"
            f"Trong {filter_scope}, chỉ số có hệ số tương quan cao nhất với "
            f"điểm hạnh phúc là **{highest_score_correlation['Chỉ số']}** "
            f"(r = {highest_score_correlation['Hệ số tương quan Pearson']:.3f}); "
            f"hệ số thấp nhất là **{lowest_score_correlation['Chỉ số']}** "
            f"(r = {lowest_score_correlation['Hệ số tương quan Pearson']:.3f}). "
            "Hệ số dương cho thấy hai chỉ số có xu hướng tăng cùng chiều trong "
            "dữ liệu; hệ số âm cho thấy xu hướng ngược chiều. Hệ số gần 0 thể "
            "hiện ít liên hệ tuyến tính hơn. Đây là tương quan, không chứng minh "
            "chỉ số đó gây ra thay đổi về hạnh phúc."
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
            strongest_pair = max(pairplot_pairs, key=lambda pair: abs(pair[2]))
            st.info(
                "**Nhận xét chi tiết**\n\n"
                f"Pairplot gồm {len(pairplot_data)} bản ghi đầy đủ, "
                f"{pairplot_data['Country'].nunique()} quốc gia và "
                f"{pairplot_data['Region'].nunique()} khu vực trong "
                f"{filter_scope}. Trong các chỉ số đang chọn, cặp có liên hệ "
                f"tuyến tính rõ nhất là **{factor_labels[strongest_pair[0]]} – "
                f"{factor_labels[strongest_pair[1]]}** "
                f"(r = {strongest_pair[2]:.3f}). Các điểm được tô màu theo "
                "khu vực để quan sát sự phân bố và chồng lấp giữa các nhóm; "
                "mối liên hệ quan sát được không khẳng định quan hệ nhân quả. "
                "Nếu chọn tất cả các năm, một quốc gia có thể xuất hiện ở "
                "nhiều điểm."
            )
