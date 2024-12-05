import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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


def get_historical_data():
   # 30분 데이터
   data = {
       '저장시간': pd.date_range(start='2018-05-10 09:30:00',
                             end='2018-05-10 10:00:00', freq='1min'),
       '내부온도': [19.5, 19.5, 19.6, 19.6, 19.7, 19.7, 19.7, 19.8, 19.8, 19.8,
                 19.8, 19.8, 19.8, 19.8, 19.8, 19.9, 19.9, 20.1, 20.2, 20.3,
                 20.4, 20.6, 20.9, 21.1, 21.3, 21.3, 21.3, 21.3, 21.2, 21.2, 21.1],
       '내부습도': [65.6, 65.5, 64.9, 64.9, 64.2, 64.2, 64.7, 64.2, 63.6, 63.5,
                 63.5, 63.5, 63.5, 63.2, 63.2, 62.5, 62.9, 63.8, 63.6, 63.9,
                 63.1, 61.9, 61.4, 61.6, 61.6, 61.3, 61.0, 60.9, 60.7, 60.6, 60.8]
   }
   return pd.DataFrame(data)


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

   st.divider()

   # 과거 30분 데이터 그래프
   st.subheader('과거 30분 내부 환경 변화')

   # 데이터 가져오기
   historical_data = get_historical_data()

   # 온도와 습도를 하나의 차트에 표시
   fig = make_subplots(specs=[[{"secondary_y": True}]])

   # 온도 데이터 추가 (주 y축)
   fig.add_trace(
       go.Scatter(
           x=historical_data['저장시간'],
           y=historical_data['내부온도'],
           name="내부 온도",
           line=dict(color="#FF4B4B")
       ),
       secondary_y=False,
   )

   # 습도 데이터 추가 (보조 y축)
   fig.add_trace(
       go.Scatter(
           x=historical_data['저장시간'],
           y=historical_data['내부습도'],
           name="내부 습도",
           line=dict(color="#4B4BFF")
       ),
       secondary_y=True,
   )

   # 레이아웃 업데이트
   fig.update_layout(
       title='내부 온도 및 습도 변화',
       xaxis_title="시간",
       height=400,
   )

   # y축 제목 업데이트
   fig.update_yaxes(title_text="온도 (°C)", secondary_y=False)
   fig.update_yaxes(title_text="습도 (%)", secondary_y=True)

   # 플로틀리 차트 표시
   st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
   main()