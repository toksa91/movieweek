import streamlit as st
import pandas as pd
import numpy as np
import io

# Set page configuration
st.set_page_config(
    page_title="MovieWeek",
    layout="wide",
)

# App title and description
st.title("🎬 MovieWeek")
st.markdown("요일별 영화 관람객 패턴을 분석하고 시각화하는 웹 앱입니다.")

try:
    # GitHub URL에서 직접 데이터 불러오기
    # 'data.csv' 파일의 raw URL
    url = 'https://raw.githubusercontent.com/toksa91/movieweek/main/data.csv'

    # CSV 파일의 헤더가 불규칙하므로, 직접 컬럼명을 지정하고 불필요한 상단 행을 건너뜁니다.
    columns = ['순위', '영화명', '개봉일', '매출액', '매출액_점유율', '매출액증감', '매출액증감율', '누적매출액',
               '관객수', '관객수증감', '관객수증감율', '누적관객수', '스크린수', '상영횟수', '대표국적',
               '국적', '제작사', '배급사', '등급', '장르', '감독', '배우']
    df = pd.read_csv(url, encoding='cp949', skiprows=8, names=columns)

    st.success("데이터를 성공적으로 불러왔습니다!")
    st.subheader("📊 데이터 분석 및 시각화 결과")

    # 필요한 컬럼만 선택
    req_cols = ['개봉일', '영화명', '관객수', '매출액']
    if '장르' in df.columns:
        req_cols.append('장르')
    df = df[req_cols].copy()

    # 컬럼명 통일
    df.rename(columns={'개봉일': '날짜'}, inplace=True)

    # 날짜 변환 & 요일 생성
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    df.dropna(subset=['날짜'], inplace=True)
    weekdays = ['월', '화', '수', '목', '금', '토', '일']
    df['요일'] = df['날짜'].dt.weekday.apply(lambda x: weekdays[x])

    # 관객수 처리
    df['관객수'] = df['관객수'].astype(str).str.replace(',', '', regex=False)
    df['관객수'] = pd.to_numeric(df['관객수'], errors='coerce').fillna(0).astype(int)

    # 매출액 처리
    df['매출액'] = df['매출액'].astype(str).str.replace(',', '', regex=False)
    df['매출액'] = pd.to_numeric(df['매출액'], errors='coerce').fillna(0).astype(int)

    # ===============================
    # 요일별 총/평균 관객수
    # ===============================
    total_audience_by_day = df.groupby('요일')['관객수'].sum().reindex(weekdays)
    daily_average_audience = df.groupby('요일')['관객수'].mean().reindex(weekdays)

    # ===============================
    # 요일별 최대/최소 영화
    # ===============================
    max_audience_by_day = df.loc[df.groupby('요일')['관객수'].idxmax()][['요일', '영화명', '관객수']]
    min_audience_by_day = df.loc[df.groupby('요일')['관객수'].idxmin()][['요일', '영화명', '관객수']]

    # ===============================
    # Streamlit columns: 총/평균 관객수
    # ===============================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### **요일별 총 관객 수**")
        st.bar_chart(total_audience_by_day)
    with col2:
        st.markdown("### **요일별 평균 관객 수**")
        st.line_chart(daily_average_audience)

    # ===============================
    # 요일별 최대/최소 영화 표시
    # ===============================
    st.markdown("### **요일별 최대 관객 영화**")
    st.dataframe(max_audience_by_day.set_index('요일'))

    st.markdown("### **요일별 최소 관객 영화**")
    st.dataframe(min_audience_by_day.set_index('요일'))

    # ===============================
    # 장르별 요일 관객수 (선택적)
    # ===============================
    if '장르' in df.columns:
        st.markdown("### **장르별 요일 관객 수**")
        genre_day = df.groupby(['장르', '요일'])['관객수'].sum().unstack(fill_value=0).reindex(columns=weekdays, fill_value=0)
        st.dataframe(genre_day)
        st.markdown("#### **장르별 요일 관객수 막대 차트**")
        st.bar_chart(genre_day.T)
    else:
        st.info("장르별 분석을 위해 '장르' 컬럼이 포함된 파일을 업로드해주세요.")

    # ===============================
    # 요일별 총 매출액 시각화
    # ===============================
    st.markdown("### **요일별 총 매출액**")
    total_sales_by_day = df.groupby('요일')['매출액'].sum().reindex(weekdays)
    st.bar_chart(total_sales_by_day)
    
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.markdown("데이터가 존재하지 않거나, URL 주소 또는 파일 형식에 문제가 있을 수 있습니다.")
