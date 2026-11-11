import pandas as pd
import os

def clean_single_file(filepath, year):
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
    
    # Xử lý giá trị thiếu (nếu có) trên từng bảng
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    
    return df

if __name__ == "__main__":
    # Danh sách các năm cần xử lý độc lập
    years = [2015, 2016, 2017, 2018, 2019]
    
    for y in years:
        path = f"data/{y}.csv"
        cleaned_df = clean_single_file(path, y)
        
        if cleaned_df is not None:
            # Lưu ra file sạch riêng cho từng năm
            output_path = f"data/{y}.csv"
            cleaned_df.to_csv(output_path, index=False)
            print(f" Đã làm sạch và lưu thành công: {output_path}")