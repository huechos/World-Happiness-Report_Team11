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
    normalized = unicodedata.normalize("NFKD", str(value).casefold())
    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents).strip()


def country_display_name(country):
    vietnamese_name = VIETNAMESE_COUNTRY_NAMES.get(country)
    if vietnamese_name and vietnamese_name != country:
        return f"{vietnamese_name} ({country})"
    return country


@st.cache_data(ttl=900)
def filter_data(years, score_min, score_max, country_query):
    data = load_all_data()
    filtered = data[
        data["Year"].isin(years)
        & data["Happiness Score"].between(score_min, score_max)
    ]
    if country_query:
        normalized_query = normalize_country_name(country_query)
        english_matches = filtered["Country"].map(
            lambda country: (
                normalize_country_name(country) == normalized_query
                if len(normalized_query) < 3
                else normalized_query in normalize_country_name(country)
            )
        )
        localized_matches = set()
        for localized_name, english_names in COUNTRY_ALIASES.items():
            normalized_localized_name = normalize_country_name(localized_name)
            if normalized_query == normalized_localized_name or (
                len(normalized_query) >= 3
                and normalized_query in normalized_localized_name
            ):
                localized_matches.update(english_names)
        if localized_matches:
            english_matches |= filtered["Country"].isin(localized_matches)
        filtered = filtered[english_matches]
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

tab_explore, tab_compare, tab_factors = st.tabs(
    ["🌐 Khám phá", "⚖️ So sánh", "📊 Yếu tố"]
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
        top_countries = filtered.nlargest(10, "Happiness Score").sort_values(
            "Happiness Score"
        )
        ranking_fig = px.bar(
            top_countries,
            x="Happiness Score",
            y="Country",
            color="Year",
            orientation="h",
            title="10 quốc gia có điểm cao nhất",
        )
        ranking_fig.update_layout(height=460)
        st.plotly_chart(ranking_fig, use_container_width=True)

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