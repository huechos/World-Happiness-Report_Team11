"""Tiền xử lý dữ liệu World Happiness Report.

Chuẩn hóa tên quốc gia và tên cột, bổ sung thông tin khu vực,
điền giá trị thiếu cho dữ liệu số và làm sạch từng file theo năm.
"""

import os
from pathlib import Path

import pandas as pd


REGION_REFERENCE_YEARS = (2015, 2016)
COUNTRY_NAME_ALIASES = {
    'Hong Kong S.A.R., China': 'Hong Kong',
    'Taiwan Province of China': 'Taiwan',
    'Northern Cyprus': 'North Cyprus',
    'Trinidad & Tobago': 'Trinidad and Tobago',
    'North Macedonia': 'Macedonia',
}
REGION_OVERRIDES = {
    'Gambia': 'Sub-Saharan Africa',
}


def build_region_mapping(data_dir):
    """Tạo mapping quốc gia-vùng từ các bảng tham chiếu có sẵn."""
    data_dir = Path(data_dir)
    region_mapping = {}

    for year in REGION_REFERENCE_YEARS:
        filepath = data_dir / f'{year}.csv'
        if not filepath.exists():
            continue

        reference_df = pd.read_csv(filepath)
        country_column = next(
            (column for column in ('Country', 'Country or region')
             if column in reference_df.columns),
            None,
        )
        if country_column is None or 'Region' not in reference_df.columns:
            continue

        reference_rows = reference_df[[country_column, 'Region']].dropna()
        for country, region in reference_rows.itertuples(index=False, name=None):
            country = str(country).strip()
            region = str(region).strip()
            existing_region = region_mapping.get(country)
            if existing_region is not None and existing_region != region:
                raise ValueError(
                    f"Quốc gia '{country}' có Region không thống nhất: "
                    f"'{existing_region}' và '{region}'."
                )
            region_mapping[country] = region

    if not region_mapping:
        raise ValueError(
            f"Không tìm thấy bảng tham chiếu có cột Country và Region trong "
            f"'{data_dir}'."
        )

    for country, reference_country in COUNTRY_NAME_ALIASES.items():
        if reference_country in region_mapping:
            region_mapping[country] = region_mapping[reference_country]
    region_mapping.update(REGION_OVERRIDES)
    return region_mapping


def add_region_column(df, region_mapping):
    """Bổ sung Region còn thiếu dựa trên tên quốc gia."""
    if 'Country' not in df.columns:
        raise ValueError("Không thể bổ sung Region: bảng không có cột Country.")

    mapped_regions = (
        df['Country'].astype('string').str.strip().map(region_mapping)
    )
    if 'Region' in df.columns:
        existing_regions = (
            df['Region'].astype('string').str.strip().replace('', pd.NA)
        )
        df['Region'] = existing_regions.fillna(mapped_regions)
    else:
        df.insert(df.columns.get_loc('Country') + 1, 'Region', mapped_regions)

    unmapped_countries = (
        df.loc[df['Region'].isna() & df['Country'].notna(), 'Country']
        .drop_duplicates()
        .tolist()
    )
    if unmapped_countries:
        print(f"Chưa tìm thấy Region cho các quốc gia: {unmapped_countries}")

    return df


def clean_single_file(filepath, year, region_mapping=None):
    """Hàm làm sạch cho từng file CSV theo năm"""
    if not os.path.exists(filepath):
        print(f"Không tìm thấy file: {filepath}")
        return None
        
    df = pd.read_csv(filepath)
    df['Year'] = year  # Giữ lại cột năm để phân biệt
    
    # Chuẩn hóa tên cột do các năm Kaggle hay đặt lệch nhau
    column_mapping = {
        'Country or region': 'Country',
        'Overall rank': 'Happiness Rank',
        'Score': 'Happiness Score',
        'GDP per capita': 'GDP per capita',
        'Economy (GDP per Capita)': 'GDP per capita',
        'Social support': 'Social support',
        'Family': 'Social support',
        'Healthy life expectancy': 'Life Expectancy',
        'Health (Life Expectancy)': 'Life Expectancy',
        'Freedom to make life choices': 'Freedom',
        'Freedom': 'Freedom',
        'Generosity': 'Generosity',
        'Perceptions of corruption': 'Perceptions of corruption',
        'Trust (Government Corruption)': 'Perceptions of corruption'
    }
    
    df = df.rename(columns=column_mapping)
    if region_mapping is None:
        region_mapping = build_region_mapping(Path(filepath).parent)
    df = add_region_column(df, region_mapping)
    
    # Xử lý giá trị thiếu (nếu có) trên từng bảng
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    
    return df

if __name__ == "__main__":
    # Danh sách các năm cần xử lý độc lập
    years = [2015, 2016, 2017, 2018, 2019]
    region_mapping = build_region_mapping("data")
    
    for y in years:
        path = Path("data") / f"{y}.csv"
        cleaned_df = clean_single_file(path, y, region_mapping)
        
        if cleaned_df is not None:
            # Lưu ra file sạch riêng cho từng năm
            output_path = f"data/{y}.csv"
            cleaned_df.to_csv(output_path, index=False)
            print(f" Đã làm sạch và lưu thành công: {output_path}")