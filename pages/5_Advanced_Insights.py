"""Trang khám phá nâng cao cho dữ liệu hạnh phúc.

Cung cấp bộ lọc ngữ cảnh, tìm kiếm tên quốc gia bằng tiếng Việt,
và ba góc nhìn: khám phá, so sánh quốc gia và phân tích yếu tố.
"""

import re
import unicodedata

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

VIETNAMESE_COUNTRY_NAMES = {
    "Afghanistan": "Afghanistan",
    "Albania": "Albania",
    "Algeria": "Algeria",
    "Angola": "Angola",
    "Argentina": "Argentina",
    "Armenia": "Armenia",
    "Australia": "Úc",
    "Austria": "Áo",
    "Azerbaijan": "Azerbaijan",
    "Bahrain": "Bahrain",
    "Bangladesh": "Bangladesh",
    "Belarus": "Belarus",
    "Belgium": "Bỉ",
    "Belize": "Belize",
    "Benin": "Benin",
    "Bhutan": "Bhutan",
    "Bolivia": "Bolivia",
    "Bosnia and Herzegovina": "Bosnia và Herzegovina",
    "Botswana": "Botswana",
    "Brazil": "Brazil",
    "Bulgaria": "Bulgaria",
    "Burkina Faso": "Burkina Faso",
    "Burundi": "Burundi",
    "Cambodia": "Campuchia",
    "Cameroon": "Cameroon",
    "Canada": "Canada",
    "Central African Republic": "Cộng hòa Trung Phi",
    "Chad": "Chad",
    "Chile": "Chile",
    "China": "Trung Quốc",
    "Colombia": "Colombia",
    "Comoros": "Comoros",
    "Congo (Brazzaville)": "Cộng hòa Congo",
    "Congo (Kinshasa)": "Cộng hòa Dân chủ Congo",
    "Costa Rica": "Costa Rica",
    "Croatia": "Croatia",
    "Cyprus": "Síp",
    "Czech Republic": "Cộng hòa Séc",
    "Denmark": "Đan Mạch",
    "Djibouti": "Djibouti",
    "Dominican Republic": "Cộng hòa Dominica",
    "Ecuador": "Ecuador",
    "Egypt": "Ai Cập",
    "El Salvador": "El Salvador",
    "Estonia": "Estonia",
    "Ethiopia": "Ethiopia",
    "Finland": "Phần Lan",
    "France": "Pháp",
    "Gabon": "Gabon",
    "Gambia": "Gambia",
    "Georgia": "Georgia",
    "Germany": "Đức",
    "Ghana": "Ghana",
    "Greece": "Hy Lạp",
    "Guatemala": "Guatemala",
    "Guinea": "Guinea",
    "Haiti": "Haiti",
    "Honduras": "Honduras",
    "Hong Kong": "Hồng Kông",
    "Hong Kong S.A.R., China": "Hồng Kông",
    "Hungary": "Hungary",
    "Iceland": "Iceland",
    "India": "Ấn Độ",
    "Indonesia": "Indonesia",
    "Iran": "Iran",
    "Iraq": "Iraq",
    "Ireland": "Ireland",
    "Israel": "Israel",
    "Italy": "Ý",
    "Ivory Coast": "Bờ Biển Ngà",
    "Jamaica": "Jamaica",
    "Japan": "Nhật Bản",
    "Jordan": "Jordan",
    "Kazakhstan": "Kazakhstan",
    "Kenya": "Kenya",
    "Kosovo": "Kosovo",
    "Kuwait": "Kuwait",
    "Kyrgyzstan": "Kyrgyzstan",
    "Laos": "Lào",
    "Latvia": "Latvia",
    "Lebanon": "Lebanon",
    "Lesotho": "Lesotho",
    "Liberia": "Liberia",
    "Libya": "Libya",
    "Lithuania": "Litva",
    "Luxembourg": "Luxembourg",
    "Macedonia": "Bắc Macedonia",
    "North Macedonia": "Bắc Macedonia",
    "Madagascar": "Madagascar",
    "Malawi": "Malawi",
    "Malaysia": "Malaysia",
    "Mali": "Mali",
    "Malta": "Malta",
    "Mauritania": "Mauritania",
    "Mauritius": "Mauritius",
    "Mexico": "Mexico",
    "Moldova": "Moldova",
    "Mongolia": "Mông Cổ",
    "Montenegro": "Montenegro",
    "Morocco": "Ma-rốc",
    "Mozambique": "Mozambique",
    "Myanmar": "Myanmar",
    "Namibia": "Namibia",
    "Nepal": "Nepal",
    "Netherlands": "Hà Lan",
    "New Zealand": "New Zealand",
    "Nicaragua": "Nicaragua",
    "Niger": "Niger",
    "Nigeria": "Nigeria",
    "North Cyprus": "Bắc Síp",
    "Northern Cyprus": "Bắc Síp",
    "Norway": "Na Uy",
    "Oman": "Oman",
    "Pakistan": "Pakistan",
    "Palestinian Territories": "Palestine",
    "Panama": "Panama",
    "Paraguay": "Paraguay",
    "Peru": "Peru",
    "Philippines": "Philippines",
    "Poland": "Ba Lan",
    "Portugal": "Bồ Đào Nha",
    "Puerto Rico": "Puerto Rico",
    "Qatar": "Qatar",
    "Romania": "Romania",
    "Russia": "Nga",
    "Rwanda": "Rwanda",
    "Saudi Arabia": "Ả Rập Xê Út",
    "Senegal": "Senegal",
    "Serbia": "Serbia",
    "Sierra Leone": "Sierra Leone",
    "Singapore": "Singapore",
    "Slovakia": "Slovakia",
    "Slovenia": "Slovenia",
    "Somalia": "Somalia",
    "Somaliland Region": "Somaliland",
    "Somaliland region": "Somaliland",
    "South Africa": "Nam Phi",
    "South Korea": "Hàn Quốc",
    "South Sudan": "Nam Sudan",
    "Spain": "Tây Ban Nha",
    "Sri Lanka": "Sri Lanka",
    "Sudan": "Sudan",
    "Suriname": "Suriname",
    "Swaziland": "Eswatini",
    "Sweden": "Thụy Điển",
    "Switzerland": "Thụy Sĩ",
    "Syria": "Syria",
    "Taiwan": "Đài Loan",
    "Taiwan Province of China": "Đài Loan",
    "Tajikistan": "Tajikistan",
    "Tanzania": "Tanzania",
    "Thailand": "Thái Lan",
    "Togo": "Togo",
    "Trinidad & Tobago": "Trinidad và Tobago",
    "Trinidad and Tobago": "Trinidad và Tobago",
    "Tunisia": "Tunisia",
    "Turkey": "Thổ Nhĩ Kỳ",
    "Turkmenistan": "Turkmenistan",
    "Uganda": "Uganda",
    "Ukraine": "Ukraine",
    "United Arab Emirates": "Các Tiểu vương quốc Ả Rập Thống nhất",
    "United Kingdom": "Vương quốc Anh",
    "United States": "Mỹ",
    "Uruguay": "Uruguay",
    "Uzbekistan": "Uzbekistan",
    "Venezuela": "Venezuela",
    "Vietnam": "Việt Nam",
    "Yemen": "Yemen",
    "Zambia": "Zambia",
    "Zimbabwe": "Zimbabwe",
}

COUNTRY_ALIASES = {
    "Mỹ": ("United States",),
    "Hoa Kỳ": ("United States",),
    "Hợp chúng quốc Hoa Kỳ": ("United States",),
    "Anh": ("United Kingdom",),
    "Anh Quốc": ("United Kingdom",),
    "Vương quốc Anh": ("United Kingdom",),
    "Úc": ("Australia",),
    "Australia": ("Australia",),
    "Hàn Quốc": ("South Korea",),
    "Đại Hàn Dân Quốc": ("South Korea",),
    "Nhật": ("Japan",),
    "Nhật Bản": ("Japan",),
    "Trung Quốc": ("China",),
    "Đài Loan": ("Taiwan", "Taiwan Province of China"),
    "Việt Nam": ("Vietnam",),
    "Lào": ("Laos",),
    "Campuchia": ("Cambodia",),
    "Thái Lan": ("Thailand",),
    "Ấn Độ": ("India",),
    "Nga": ("Russia",),
    "Pháp": ("France",),
    "Đức": ("Germany",),
    "Ý": ("Italy",),
    "Tây Ban Nha": ("Spain",),
    "Hà Lan": ("Netherlands",),
    "Bỉ": ("Belgium",),
    "Thụy Sĩ": ("Switzerland",),
    "Thụy Điển": ("Sweden",),
    "Na Uy": ("Norway",),
    "Đan Mạch": ("Denmark",),
    "Phần Lan": ("Finland",),
    "Ba Lan": ("Poland",),
    "Séc": ("Czech Republic",),
    "Cộng hòa Séc": ("Czech Republic",),
    "Thổ Nhĩ Kỳ": ("Turkey",),
    "Ai Cập": ("Egypt",),
    "Nam Phi": ("South Africa",),
    "Ả Rập Xê Út": ("Saudi Arabia",),
    "Hồng Kông": ("Hong Kong", "Hong Kong S.A.R., China"),
    "Bắc Macedonia": ("Macedonia", "North Macedonia"),
    "Síp": ("Cyprus",),
    "Bồ Đào Nha": ("Portugal",),
    "Mexico": ("Mexico",),
    "Brazil": ("Brazil",),
    "Canada": ("Canada",),
}

for country, localized_name in VIETNAMESE_COUNTRY_NAMES.items():
    if localized_name != country:
        COUNTRY_ALIASES[localized_name] = tuple(
            set(COUNTRY_ALIASES.get(localized_name, ())) | {country}
        )

COUNTRY_ALIASES.update(
    {
        "Hoa Kỳ": ("United States",),
        "USA": ("United States",),
        "US": ("United States",),
        "Miến Điện": ("Myanmar",),
    }
)


def normalize_country_name(value):
    """Chuẩn hóa tên quốc gia về chữ thường, bỏ dấu để hỗ trợ tìm kiếm."""
    normalized = unicodedata.normalize("NFKD", str(value).casefold())
    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents).strip()


def country_display_name(country):
    """Trả về tên Việt hóa kèm tên gốc bằng tiếng Anh nếu có thể."""
    vietnamese_name = VIETNAMESE_COUNTRY_NAMES.get(country)
    if vietnamese_name and vietnamese_name != country:
        return f"{vietnamese_name} ({country})"
    return country


@st.cache_data(ttl=900)
def filter_data(years, score_min, score_max, selected_countries):
    """Lọc dữ liệu theo năm, khoảng điểm hạnh phúc và quốc gia."""
    data = load_all_data()
    filtered = data[
        data["Year"].isin(years)
        & data["Happiness Score"].between(score_min, score_max)
    ]
    if selected_countries:
        filtered = filtered[filtered["Country"].isin(selected_countries)]
    return filtered


data = load_all_data()
if data.empty:
    st.error("Không thể tải dữ liệu. Kiểm tra thư mục data.")
    st.stop()

score_min = float(data["Happiness Score"].min())
score_max = float(data["Happiness Score"].max())

with st.sidebar:
    # Bộ lọc chung điều khiển dữ liệu cho toàn bộ ba tab.
    st.header("Bộ lọc dữ liệu")
    selected_years = st.multiselect("Năm báo cáo", YEARS, default=YEARS)
    score_range = st.slider(
        "Khoảng điểm hạnh phúc",
        min_value=score_min,
        max_value=score_max,
        value=(score_min, score_max),
        step=0.1,
    )
    selected_filter_countries = st.multiselect(
        "Chọn quốc gia",
        sorted(data["Country"].dropna().unique()),
        default=[],
        format_func=country_display_name,
        placeholder="Tìm và chọn nhiều quốc gia",
    )

filtered = filter_data(
    tuple(selected_years),
    score_range[0],
    score_range[1],
    tuple(selected_filter_countries),
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

tab_explore, tab_compare, tab_factors = st.tabs(
    ["🌐 Khám phá", "⚖️ So sánh", "📊 Yếu tố"]
)

# Tab khám phá: hiển thị phân tán giữa điểm hạnh phúc và yếu tố đã chọn.
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

        chart_data = filtered[
            ["Country", "Year", "Happiness Score", selected_factor]
        ].dropna()
        st.markdown("**Nhận xét về biểu đồ**")
        if len(chart_data) < 2:
            st.info("Cần ít nhất hai quan sát có đủ dữ liệu để phân tích biểu đồ.")
        else:
            correlation_value = chart_data[
                ["Happiness Score", selected_factor]
            ].corr().iloc[0, 1]

            if pd.isna(correlation_value):
                st.info(
                    "Chưa thể xác định tương quan vì một trong hai chỉ số "
                    "không có độ biến thiên."
                )
            else:
                if correlation_value >= 0.7:
                    relationship = "tương quan thuận mạnh"
                elif correlation_value >= 0.4:
                    relationship = "tương quan thuận vừa"
                elif correlation_value > 0.2:
                    relationship = "tương quan thuận yếu"
                elif correlation_value >= -0.2:
                    relationship = "hầu như không có tương quan tuyến tính rõ ràng"
                elif correlation_value >= -0.4:
                    relationship = "tương quan nghịch yếu"
                elif correlation_value > -0.7:
                    relationship = "tương quan nghịch vừa"
                else:
                    relationship = "tương quan nghịch mạnh"

                highest_row = chart_data.loc[
                    chart_data["Happiness Score"].idxmax()
                ]
                lowest_row = chart_data.loc[
                    chart_data["Happiness Score"].idxmin()
                ]
                st.markdown(
                    f"- **Mối liên hệ:** Điểm hạnh phúc và **{selected_factor}** có "
                    f"{relationship} (r = **{correlation_value:.3f}**). Đây là tương "
                    "quan, không khẳng định yếu tố này trực tiếp gây ra thay đổi."
                )
                st.markdown(
                    f"- **Điểm cao nhất:** "
                    f"{country_display_name(highest_row['Country'])} "
                    f"({int(highest_row['Year'])}), "
                    f"**{highest_row['Happiness Score']:.3f}**."
                )
                st.markdown(
                    f"- **Điểm thấp nhất:** "
                    f"{country_display_name(lowest_row['Country'])} "
                    f"({int(lowest_row['Year'])}), "
                    f"**{lowest_row['Happiness Score']:.3f}**."
                )
                st.markdown(
                    f"- **Phạm vi dữ liệu:** {len(chart_data)} quan sát; "
                    f"điểm hạnh phúc trung bình "
                    f"**{chart_data['Happiness Score'].mean():.3f}**, "
                    f"{selected_factor} trung bình "
                    f"**{chart_data[selected_factor].mean():.3f}** "
                    f"(dao động {chart_data[selected_factor].min():.3f}–"
                    f"{chart_data[selected_factor].max():.3f})."
                )

    with ranking_col:
        latest_year = int(filtered["Year"].max())
        latest_data = filtered[
            (filtered["Year"] == latest_year)
            & filtered["Happiness Score"].notna()
        ]
        top_countries = latest_data.nlargest(10, "Happiness Score").copy()

        top_countries["Hạng"] = range(1, len(top_countries) + 1)
        top_countries["Quốc gia"] = top_countries["Country"].map(
            country_display_name
        )
        top_countries["Năm"] = latest_year
        top_table = top_countries[
            [
                "Hạng",
                "Quốc gia",
                "Năm",
                "Happiness Score",
            ]
        ].rename(columns={"Happiness Score": "Điểm hạnh phúc"})

        top_table["Điểm hạnh phúc"] = top_table["Điểm hạnh phúc"].map(
            lambda value: f"{value:.3f}"
        )

        st.subheader("Top 10 quốc gia")
        st.caption(
            f"Các quốc gia có điểm cao nhất năm {latest_year} "
            "trong phạm vi bộ lọc."
        )
        st.dataframe(
            top_table,
            hide_index=True,
            use_container_width=True,
            height=380,
        )

with tab_compare:
    # Tab so sánh: theo dõi xu hướng điểm hạnh phúc của các quốc gia.
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
        format_func=country_display_name,
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
        st.markdown("**Nhận xét biểu đồ so sánh**")
        comparison_data = comparison.dropna(
            subset=["Year", "Happiness Score"]
        ).sort_values("Year")
        for country, country_data in comparison_data.groupby("Country"):
            first = country_data.iloc[0]
            last = country_data.iloc[-1]
            if len(country_data) < 2:
                st.markdown(
                    f"- **{country_display_name(country)}:** chỉ có dữ liệu năm "
                    f"{int(first['Year'])}, chưa đủ để nhận xét xu hướng."
                )
                continue

            change = last["Happiness Score"] - first["Happiness Score"]
            if change > 0.05:
                trend = "tăng"
            elif change < -0.05:
                trend = "giảm"
            else:
                trend = "gần như ổn định"
            highest = country_data.loc[
                country_data["Happiness Score"].idxmax()
            ]
            lowest = country_data.loc[
                country_data["Happiness Score"].idxmin()
            ]
            st.markdown(
                f"- **{country_display_name(country)}:** điểm {trend} "
                f"{abs(change):.3f} từ {int(first['Year'])} "
                f"({first['Happiness Score']:.3f}) đến {int(last['Year'])} "
                f"({last['Happiness Score']:.3f}); cao nhất "
                f"{highest['Happiness Score']:.3f} năm {int(highest['Year'])}, "
                f"thấp nhất {lowest['Happiness Score']:.3f} năm "
                f"{int(lowest['Year'])}."
            )
    else:
        st.info("Chọn ít nhất một quốc gia để xem biểu đồ so sánh.")

with tab_factors:
    # Tab yếu tố: phân tích từng yếu tố và tổng hợp tương quan của toàn bộ nhóm.
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
    st.markdown(f"**Nhận xét biểu đồ: {factor} và điểm hạnh phúc**")
    if len(factor_data) < 2:
        st.info("Cần ít nhất hai quan sát có đủ dữ liệu để phân tích biểu đồ.")
    else:
        factor_correlation = factor_data[
            [factor, "Happiness Score"]
        ].corr().iloc[0, 1]
        if pd.isna(factor_correlation):
            st.info(
                "Chưa thể xác định tương quan vì một trong hai chỉ số "
                "không có độ biến thiên."
            )
        else:
            if factor_correlation >= 0.7:
                relationship = "tương quan thuận mạnh"
            elif factor_correlation >= 0.4:
                relationship = "tương quan thuận vừa"
            elif factor_correlation > 0.2:
                relationship = "tương quan thuận yếu"
            elif factor_correlation >= -0.2:
                relationship = "hầu như không có tương quan tuyến tính rõ ràng"
            elif factor_correlation >= -0.4:
                relationship = "tương quan nghịch yếu"
            elif factor_correlation > -0.7:
                relationship = "tương quan nghịch vừa"
            else:
                relationship = "tương quan nghịch mạnh"

            highest_factor = factor_data.loc[factor_data[factor].idxmax()]
            lowest_factor = factor_data.loc[factor_data[factor].idxmin()]
            st.markdown(
                f"- **Mối liên hệ:** {factor} và điểm hạnh phúc có "
                f"{relationship} (r = **{factor_correlation:.3f}**). "
                "Tương quan không đồng nghĩa với quan hệ nhân quả."
            )
            st.markdown(
                f"- **Giá trị yếu tố cao nhất:** "
                f"{country_display_name(highest_factor['Country'])} "
                f"({int(highest_factor['Year'])}), {factor} = "
                f"**{highest_factor[factor]:.3f}**, điểm hạnh phúc "
                f"**{highest_factor['Happiness Score']:.3f}**."
            )
            st.markdown(
                f"- **Giá trị yếu tố thấp nhất:** "
                f"{country_display_name(lowest_factor['Country'])} "
                f"({int(lowest_factor['Year'])}), {factor} = "
                f"**{lowest_factor[factor]:.3f}**, điểm hạnh phúc "
                f"**{lowest_factor['Happiness Score']:.3f}**."
            )

    correlation = (
        filtered[["Happiness Score"] + factor_options]
        .corr(numeric_only=True)["Happiness Score"]
        .drop("Happiness Score")
        .sort_values(ascending=False)
        .rename_axis("Yếu tố")
        .reset_index(name="Hệ số tương quan")
    )
    correlation_fig = px.bar(
        correlation,
        x="Hệ số tương quan",
        y="Yếu tố",
        orientation="h",
        title="Tương quan với điểm hạnh phúc",
    )
    correlation_fig.update_layout(height=360)
    st.plotly_chart(correlation_fig, use_container_width=True)
    st.markdown("**Nhận xét biểu đồ tương quan**")
    valid_correlations = correlation.dropna(subset=["Hệ số tương quan"])
    if valid_correlations.empty:
        st.info("Chưa đủ dữ liệu để so sánh tương quan giữa các yếu tố.")
    else:
        strongest = valid_correlations.loc[
            valid_correlations["Hệ số tương quan"].abs().idxmax()
        ]
        if strongest["Hệ số tương quan"] > 0:
            direction = "thuận"
        elif strongest["Hệ số tương quan"] < 0:
            direction = "nghịch"
        else:
            direction = "không có"
        st.markdown(
            f"- Yếu tố có tương quan mạnh nhất theo trị tuyệt đối là "
            f"**{strongest['Yếu tố']}** ({direction}, "
            f"r = **{strongest['Hệ số tương quan']:.3f}**)."
        )
        positive = valid_correlations[
            valid_correlations["Hệ số tương quan"] > 0
        ]
        negative = valid_correlations[
            valid_correlations["Hệ số tương quan"] < 0
        ]
        st.markdown(
            f"- Trong {len(valid_correlations)} yếu tố, có "
            f"**{len(positive)}** yếu tố tương quan thuận và "
            f"**{len(negative)}** yếu tố tương quan nghịch với điểm hạnh phúc. "
            "Kết quả mô tả mối liên hệ trong dữ liệu, không chứng minh nguyên nhân."
        )