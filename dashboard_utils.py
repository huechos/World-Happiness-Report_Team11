from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
YEARS = [2015, 2016, 2017, 2018, 2019]

COLUMN_ALIASES = {
    "Country or region": "Country",
    "Happiness.Rank": "Happiness Rank",
    "Overall rank": "Happiness Rank",
    "Happiness.Score": "Happiness Score",
    "Economy (GDP per Capita)": "GDP per capita",
    "Economy..GDP.per.Capita.": "GDP per capita",
    "Family": "Social support",
    "Health (Life Expectancy)": "Life Expectancy",
    "Health..Life.Expectancy.": "Life Expectancy",
    "Healthy life expectancy": "Life Expectancy",
    "Trust (Government Corruption)": "Perceptions of corruption",
    "Trust..Government.Corruption.": "Perceptions of corruption",
}


@st.cache_data(ttl=3600)
def load_all_data() -> pd.DataFrame:
    frames = []
    core_columns = [
        "Country", "Region", "Happiness Rank", "Happiness Score",
        "GDP per capita", "Social support", "Life Expectancy",
        "Freedom", "Generosity", "Perceptions of corruption", "Year",
    ]
    for year in YEARS:
        path = DATA_DIR / f"{year}.csv"
        if not path.exists():
            continue
        frame = pd.read_csv(path).rename(columns=COLUMN_ALIASES)
        frame["Year"] = year
        for column in core_columns:
            if column not in frame:
                frame[column] = pd.NA
        frames.append(frame[core_columns])

    if not frames:
        return pd.DataFrame(columns=core_columns)

    data = pd.concat(frames, ignore_index=True)
    numeric_columns = [
        "Happiness Rank", "Happiness Score", "GDP per capita",
        "Social support", "Life Expectancy", "Freedom", "Generosity",
        "Perceptions of corruption",
    ]
    data[numeric_columns] = data[numeric_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    return data.drop_duplicates(subset=["Country", "Year"]).sort_values(
        ["Year", "Happiness Rank"], na_position="last"
    )


@st.cache_data(ttl=3600)
def summarize_year(data: pd.DataFrame, year: int) -> pd.DataFrame:
    return data.loc[data["Year"] == year].copy()


def apply_theme():
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] { background: transparent; }
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #e0f2fe, #dbeafe);
            border: 1px solid #93c5fd;
            border-radius: 16px;
            padding: 14px 16px;
        }
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] p {
            color: #334155 !important;
            font-weight: 600;
        }
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] div {
            color: #0f172a !important;
            font-weight: 700;
        }
        [data-testid="stMetricDelta"] {
            color: #166534 !important;
        }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            height: 46px;
            padding: 0 18px;
            border-radius: 10px 10px 0 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
