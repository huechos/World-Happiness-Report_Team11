"""Trang chủ của dashboard World Happiness Report.

Khởi tạo giao diện chung, tải dữ liệu tổng quan, hiển thị số liệu nhanh
và cung cấp liên kết điều hướng đến các trang phân tích.
"""

import pandas as pd
import streamlit as st

from dashboard_utils import DATA_DIR, YEARS, apply_theme, load_all_data


st.set_page_config(
    page_title="World Happiness Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

# CSS tùy chỉnh tạo giao diện banner, thẻ điều hướng và phần chân trang.
st.markdown(
    """
    <style>
    .home-hero {
        position: relative;
        overflow: hidden;
        padding: 2.4rem 2.6rem;
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 24px;
        background:
            radial-gradient(circle at 88% 18%, rgba(45, 212, 191, 0.30), transparent 25%),
            linear-gradient(120deg, #10243a 0%, #174a68 55%, #147d78 100%);
        color: #f8fafc;
        box-shadow: 0 18px 42px rgba(15, 42, 63, 0.18);
    }
    .home-hero .eyebrow {
        margin: 0 0 0.75rem;
        color: #99f6e4;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }
    .home-hero h1 {
        max-width: 780px;
        margin: 0;
        color: #ffffff;
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.12;
        letter-spacing: -0.035em;
    }
    .home-hero .description {
        max-width: 760px;
        margin: 1rem 0 0;
        color: #dbeafe;
        font-size: 1.08rem;
        line-height: 1.65;
    }
    .home-hero .hero-tag {
        display: inline-block;
        margin-top: 1.45rem;
        padding: 0.4rem 0.8rem;
        border: 1px solid rgba(204, 251, 241, 0.36);
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.20);
        color: #ecfeff;
        font-size: 0.88rem;
    }
    .home-section-label {
        margin: 0 0 0.25rem;
        color: #0f766e;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .home-section-title {
        margin: 0 0 1.1rem;
        color: #0f172a;
        font-size: 1.7rem;
        font-weight: 750;
        letter-spacing: -0.025em;
    }
    .home-nav-card {
        display: block;
        min-height: 176px;
        margin-bottom: 0.9rem;
        padding: 1.25rem 1.35rem;
        border: 1px solid #dbe5ed;
        border-radius: 18px;
        background: linear-gradient(160deg, #ffffff 15%, #f3f8fb 100%);
        color: #0f172a !important;
        text-decoration: none !important;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.045);
        transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
    }
    .home-nav-card:hover {
        transform: translateY(-3px);
        border-color: #5eead4;
        box-shadow: 0 14px 28px rgba(15, 118, 110, 0.13);
    }
    .home-nav-card .card-icon {
        display: block;
        margin-bottom: 0.65rem;
        font-size: 1.45rem;
    }
    .home-nav-card strong {
        display: block;
        margin-bottom: 0.38rem;
        color: #102a43;
        font-size: 1.05rem;
    }
    .home-nav-card .card-description {
        display: block;
        min-height: 2.6rem;
        color: #526579;
        font-size: 0.91rem;
        line-height: 1.45;
    }
    .home-nav-card .card-link {
        display: block;
        margin-top: 0.7rem;
        color: #0f766e;
        font-size: 0.88rem;
        font-weight: 700;
    }
    .home-footer {
        margin-top: 2.4rem;
        padding: 1rem 0 0.3rem;
        border-top: 1px solid #e2e8f0;
        color: #64748b;
        font-size: 0.84rem;
        text-align: center;
    }
    </style>

    <section class="home-hero">
        <p class="eyebrow">World Happiness Report · Nhóm 11</p>
        <h1>Khám phá bức tranh hạnh phúc toàn cầu</h1>
        <p class="description">
            So sánh các quốc gia, theo dõi biến động qua từng năm và tìm hiểu
            những yếu tố kinh tế - xã hội gắn với mức độ hạnh phúc.
        </p>
        <span class="hero-tag">🌍 Dữ liệu 2015–2019 · Trực quan hóa dữ liệu</span>
    </section>
    """,
    unsafe_allow_html=True,
)

data = load_all_data()
if data.empty:
    st.warning("Chưa có dữ liệu để tạo phần tổng quan. Hãy kiểm tra thư mục data.")
else:
    # Tổng hợp số liệu từ năm mới nhất để hiển thị trong hàng metric.
    latest_year = int(data["Year"].max())
    latest_data = data.loc[data["Year"] == latest_year]
    latest_score = latest_data["Happiness Score"].mean()
    score_label = f"{latest_score:.2f}" if pd.notna(latest_score) else "—"

    st.write("")
    metric_cols = st.columns(4)
    metric_cols[0].metric("Năm dữ liệu mới nhất", latest_year)
    metric_cols[1].metric(
        "Quốc gia trong năm",
        f"{latest_data['Country'].nunique():,}",
    )
    metric_cols[2].metric(
        "Điểm hạnh phúc trung bình",
        score_label,
    )
    metric_cols[3].metric(
        "Khu vực",
        f"{latest_data['Region'].nunique():,}",
    )

st.markdown(
    """
    <p class="home-section-label">Bắt đầu khám phá</p>
    <h2 class="home-section-title">Đi đến nội dung bạn quan tâm</h2>
    """,
    unsafe_allow_html=True,
)

navigation_cards = [
    (
        "📊",
        "Overview",
        "Tổng quan theo năm, xem bảng dữ liệu và chọn khu vực trên quả địa cầu.",
        "/Overview",
    ),
    (
        "📈",
        "Trends",
        "Theo dõi xu hướng theo thời gian và tương quan giữa các chỉ số.",
        "/Trends",
    ),
    (
        "🌎",
        "Regional Analysis",
        "So sánh khu vực, chọn nhiều vùng và đối chiếu các quốc gia.",
        "/Regional_Analysis",
    ),
    (
        "🔑",
        "Key Factors",
        "Khám phá ma trận tương quan và mối liên hệ giữa các yếu tố.",
        "/Key_Factors",
    ),
    (
        "🔎",
        "Advanced Insights",
        "Lọc dữ liệu và tìm hiểu sâu hơn qua các góc nhìn tương tác.",
        "/Advanced_Insights",
    ),
]

# Tạo thẻ điều hướng theo từng nhóm ba cột.
for row_start in range(0, len(navigation_cards), 3):
    columns = st.columns(3)
    for column, card in zip(columns, navigation_cards[row_start : row_start + 3]):
        icon, title, description, href = card
        column.markdown(
            f"""
            <a class="home-nav-card" href="{href}">
                <span class="card-icon">{icon}</span>
                <strong>{title}</strong>
                <span class="card-description">{description}</span>
                <span class="card-link">Mở trang <span aria-hidden="true">→</span></span>
            </a>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <p class="home-section-label">Dữ liệu</p>
    <h2 class="home-section-title">Xem nhanh báo cáo theo năm</h2>
    """,
    unsafe_allow_html=True,
)
selected_year_preview = st.selectbox(
    "Chọn năm dữ liệu",
    YEARS,
    index=len(YEARS) - 1,
    key="home_preview_year",
)
preview_file_path = DATA_DIR / f"{selected_year_preview}.csv"

if not preview_file_path.exists():
    st.warning(f"Không tìm thấy file dữ liệu `{preview_file_path.name}`.")
else:
    try:
        preview_data = pd.read_csv(preview_file_path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        st.error(f"Không thể đọc dữ liệu năm {selected_year_preview}: {error}")
    else:
        info_col, detail_col = st.columns([1, 2])
        info_col.metric("Số quốc gia", f"{len(preview_data):,}")
        info_col.metric("Số chỉ số", f"{len(preview_data.columns):,}")
        detail_col.caption(
            f"Bản xem trước báo cáo năm {selected_year_preview}. "
            "Mở Overview để xem toàn bộ bảng và lọc theo khu vực."
        )
        with st.expander("Xem 5 dòng dữ liệu đầu tiên", expanded=False):
            st.dataframe(
                preview_data.head(),
                use_container_width=True,
                hide_index=True,
            )

st.markdown(
    """
    <footer class="home-footer">
        Phát triển bởi Nhóm 11 · KHMT 18-01 · Đại học Đại Nam · 2026
    </footer>
    """,
    unsafe_allow_html=True,
)
