import streamlit as st
import pandas as pd
import datetime

def get_sensor_data(target_time):
    # 실제 데이터는 여기서 가져오게 됩니다
    data = {
        'internal_temp': 21.1,
        'internal_humidity': 60.8,
        'external_temp': 15.4,
        'wind_direction': '좌',
        'wind_speed': 1.1,
        'dew_point': 12.7,
        'solar_radiation': 247
    }
    return data

def main():
    st.title('익산 토마토셋 대시보드')

    # 현재 시간 표시 (여기서는 특정 시점으로 고정)
    target_time = "2018-05-10 10:00"
    st.write(f"조회 시간: {target_time}")

    st.divider()

    # 센서 데이터 가져오기
    sensor_data = get_sensor_data(target_time)

    # 1. 현재 내부 환경 데이터
    st.subheader('내부 환경')
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="내부 온도", value=f"{sensor_data['internal_temp']} °C")
    with col2:
        st.metric(label="내부 습도", value=f"{sensor_data['internal_humidity']} %")

    # 2. 외부 환경 데이터
    st.subheader('외부 환경')
    col3, col4, col5, col6 = st.columns(4)
    
    with col3:
        st.metric(label="외부 온도", value=f"{sensor_data['external_temp']} °C")
    with col4:
        st.metric(label="풍향/풍속", 
                 value=f"{sensor_data['wind_direction']} {sensor_data['wind_speed']}m/s")
    with col5:
        st.metric(label="이슬점", value=f"{sensor_data['dew_point']} °C")
    with col6:
        st.metric(label="누적일사량", value=f"{sensor_data['solar_radiation']} J/cm²")

if __name__ == '__main__':
    main()