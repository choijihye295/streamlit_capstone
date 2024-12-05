import streamlit as st
import pandas as pd
import datetime

def main():
    st.title('익산 토마토셋 대시보드')
    
    # 현재 시간 표시 (여기서는 특정 시점으로 고정)
    target_time = "2018-05-10 10:00"
    st.write(f"조회 시간: {target_time}")

    # 1. 현재 내부 환경 데이터
    st.subheader('내부 환경')
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="내부 온도", value=f"21.1 °C")
    with col2:
        st.metric(label="내부 습도", value=f"60.8 %")

    st.divider()

    # 2. 외부 환경 데이터
    st.subheader('외부 환경')
    col3, col4, col5, col6 = st.columns(4)
    
    with col3:
        st.metric(label="외부 온도", value=f"15.4 °C")
    with col4:
        st.metric(label="풍향/풍속", value=f"좌 {1.1}m/s")
    with col5:
        st.metric(label="이슬점", value=f"12.7 °C")
    with col6:
        st.metric(label="누적일사량", value=f"{247} W/m²")

if __name__ == '__main__':
    main()