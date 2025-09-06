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

# File uploader widget
uploaded_file = st.file_uploader(
    "CSV 또는 Excel 파일을 업로드하세요.",
    type=["csv", "xlsx"],
    help="필요한 컬럼: 날짜, 영화명, 관객수, 매출액, 장르(선택)"
)

if uploaded_file:
    try:
        # 파일 형식에 따라 데이터프레임으로 불러오기
        if uploaded_file.name.endswith('.csv'):
            # CSV 파일의 헤더가 불규칙하므로, 직접 컬럼명을 지정하고 불필요한 상단 행을 건너뜁니다.
            file_contents = uploaded_file.getvalue().decode('cp949', errors='replace')
            file_stream = io.StringIO(file_contents)
            
            # 헤더를 직접 지정하여 불필요한 행 건너뛰기
            columns = ['순위', '영화명', '개봉일', '매출액', '매출액_점유율', '매출액증감', '매출액증감율', '누적매출액',
                       '관객수', '관객수증감', '관객수증감율', '누적관객수', '스크린수', '상영횟수', '대표국적',
                       '국적', '제작사', '배급사', '등급', '장르', '감독', '배우']
            df = pd.read_csv(file_stream, skiprows=8, names=columns)
        else: # .xlsx
            # Excel 파일의 경우, 첫 7행을 건너뛰고 헤더를 읽어옵니다.
            df = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=7)

        st.success("파일 업로드 성공!")
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
        st.error(f"오류가 발생했습니다: {e}")
        st.markdown("업로드한 파일이 '일별 박스오피스' 데이터 형식을 따르고 있는지 확인해주세요.")

# Initial prompt before file upload
else:
    st.info("좌측 상단의 **`Browse files`** 버튼을 눌러 영화진흥위원회 데이터를 업로드해주세요.")
    st.markdown("---")
    st.markdown("#### **데이터 다운로드 방법**")
    st.markdown(
        "영화진흥위원회 KOBIS 웹사이트 (http://www.kobis.or.kr)에서 `통계 > 일별 박스오피스` 메뉴로 들어가 "
        "원하는 기간의 CSV/Excel 파일을 다운로드할 수 있습니다."
    )
