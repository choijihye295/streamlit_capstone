import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import numpy as np
import os  # 이 줄을 추가

# 페이지 설정 (스크립트 최상단에 위치)
st.set_page_config(
    page_title="익산 토마토셋 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 세션 상태 초기화
if 'update_counter' not in st.session_state:
    st.session_state.update_counter = 0

# CSS 스타일은 동일하게 유지...
st.markdown("""
    <style>
        .main > div {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .block-container {
            padding: 1rem 2rem;
            max-width: 100%;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .time-display {
            position: fixed;
            top: 0.5rem;
            right: 1rem;
            background-color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-size: 0.9rem;
            color: #666;
            z-index: 1000;
        }
        .custom-title {
            margin-bottom: 2rem;
        }
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
            height: 100%;
            margin-bottom: 1rem; /* 카드 간격 조정 */
        }
        .metric-label {
            color: #666;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        .metric-value {
            color: #111;
            margin: 0;
            font-size: 1.5rem;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# 전역 변수로 상태 관리
if 'current_time' not in st.session_state:
    st.session_state.current_time = pd.Timestamp('2018-05-10 10:00:00')

def get_current_time():
    """현재 시간 업데이트 및 반환"""
    try:
        # predictions.csv 파일 읽기
        predictions = pd.read_csv("predictions.csv")
        predictions['예측시간'] = pd.to_datetime(predictions['예측시간'])
        
        # 현재 시간을 예측 시간의 1분 전으로 설정
        if not predictions.empty:
            next_time = st.session_state.current_time + pd.Timedelta(minutes=1)
            
            # 다음 시간이 예측 시간 범위 내에 있으면 시간 업데이트
            if next_time < predictions['예측시간'].max():
                st.session_state.current_time = next_time
                
        return st.session_state.current_time
        
    except Exception as e:
        print(f"시간 업데이트 오류: {str(e)}")
        return st.session_state.current_time

def get_sensor_data():
    """최신 센서 데이터 읽기"""
    try:
        data = pd.read_csv("sensor_data.csv")
        data['저장시간'] = pd.to_datetime(data['저장시간'])
        current_time = get_current_time()
        
        # 현재 시간에 해당하는 데이터 찾기
        latest_data = data[data['저장시간'] == current_time].iloc[0]
        
        return {
            'internal_temp': round(float(latest_data['내부온도']), 1),
            'internal_humidity': round(float(latest_data['내부습도']), 1),
            'external_temp': round(float(latest_data['외부온도']), 1),
            'wind_direction': '좌', 
            'wind_speed': round(float(latest_data['풍속']), 1),
            'dew_point': round(float(latest_data['이슬점']), 1),
            'solar_radiation': int(latest_data['누적일사량'])
        }
    except Exception as e:
        st.error(f"센서 데이터 로드 오류: {str(e)}")
        return None

def get_historical_data():
    """과거 30분 데이터 읽기"""
    try:
        data = pd.read_csv("sensor_data.csv")
        data['저장시간'] = pd.to_datetime(data['저장시간'])
        
        current_time = get_current_time()
        start_time = current_time - pd.Timedelta(minutes=30)
        
        # 현재 시간까지의 데이터만 반환
        return data[
            (data['저장시간'] >= start_time) & 
            (data['저장시간'] <= current_time)
        ]
        
    except Exception as e:
        st.error(f"과거 데이터 로드 오류: {str(e)}")
        return None

def get_prediction_data():
    """예측 데이터 읽기"""
    try:
        # predictions.csv 파일이 있는지 확인
        if not os.path.exists("predictions.csv"):
            return None
            
        # predictions.csv 파일 읽기
        predictions = pd.read_csv("predictions.csv")
        predictions['예측시간'] = pd.to_datetime(predictions['예측시간'])
        
        # 현재 시간 이후의 예측 데이터만 반환
        current_time = get_current_time()
        future_predictions = predictions[predictions['예측시간'] > current_time]
        
        if future_predictions.empty:
            return None
            
        return future_predictions
        
    except Exception as e:
        st.error(f"예측 데이터 로드 오류: {str(e)}")
        return None

def create_metric_card(label, value):
    return f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """

def create_combined_graph(historical_data, prediction_data):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 현재 시간 가져오기
    current_time = get_current_time()
    
    # 실제 데이터 표시
    fig.add_trace(
        go.Scatter(
            x=historical_data['저장시간'],
            y=historical_data['내부온도'],
            name="실제 온도",
            line=dict(color="#FF4B4B", width=2)
        ),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(
            x=historical_data['저장시간'],
            y=historical_data['내부습도'],
            name="실제 습도",
            line=dict(color="#4B4BFF", width=2)
        ),
        secondary_y=True,
    )

    # 예측 데이터가 있는 경우에만 표시
    if prediction_data is not None and not prediction_data.empty:
        # 현재 시점과 첫 예측 시점을 연결하기 위한 포인트 추가
        last_real_temp = historical_data['내부온도'].iloc[-1]
        last_real_humid = historical_data['내부습도'].iloc[-1]
        first_pred_time = prediction_data['예측시간'].iloc[0]
        
        # 연결 포인트 추가
        connect_times = [current_time, first_pred_time]
        connect_temps = [last_real_temp, prediction_data['예측온도'].iloc[0]]
        connect_humids = [last_real_humid, prediction_data['예측습도'].iloc[0]]
        
        # 온도 연결선
        fig.add_trace(
            go.Scatter(
                x=connect_times,
                y=connect_temps,
                name="예측 온도",
                line=dict(color="#FF4B4B", width=2, dash='dash'),
                showlegend=False
            ),
            secondary_y=False,
        )
        
        # 습도 연결선
        fig.add_trace(
            go.Scatter(
                x=connect_times,
                y=connect_humids,
                name="예측 습도",
                line=dict(color="#4B4BFF", width=2, dash='dash'),
                showlegend=False
            ),
            secondary_y=True,
        )
        
        # # 예측선 추가
        # fig.add_trace(
        #     go.Scatter(
        #         x=prediction_data['예측시간'],
        #         y=prediction_data['예측온도'],
        #         name="예측 온도",
        #         line=dict(color="#FF4B4B", width=2, dash='dash')
        #     ),
        #     secondary_y=False,
        # )
        
        # fig.add_trace(
        #     go.Scatter(
        #         x=prediction_data['예측시간'],
        #         y=prediction_data['예측습도'],
        #         name="예측 습도",
        #         line=dict(color="#4B4BFF", width=2, dash='dash')
        #     ),
        #     secondary_y=True,
        # )

    # 레이아웃 설정
    fig.update_layout(
        hovermode="x unified",  # x축에 따라 툴팁이 통합되어 표시
        margin=dict(l=80, r=80, t=50, b=50),
        autosize=False,  # 자동 크기 조정 비활성화
        width=1200,      # 그래프 너비 설정
        height=700,  # 고정 높이 설정
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='lightgray',
            title_text="온도 (°C)"
        ),
        yaxis2=dict(
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='lightgray',
            title_text="습도 (%)"
        )
    )

    # 현재 시점 표시 선
    fig.update_layout(
        shapes=[
            dict(
                type="line",
                xref="x",
                yref="paper",
                x0=historical_data['저장시간'].iloc[-1],
                y0=0,
                x1=historical_data['저장시간'].iloc[-1],
                y1=1,
                line=dict(
                    color="gray",
                    width=1,
                    dash="dot",
                )
            )
        ],
        annotations=[
            dict(
                x=historical_data['저장시간'].iloc[-1],
                y=1.05,
                xref="x",
                yref="paper",
                text="현재",
                showarrow=False,
                font=dict(size=12)
            )
        ]
    )

    return fig


def main():
    # 데이터 로드
    current_time = get_current_time()  # 현재 시간 가져오기
    sensor_data = get_sensor_data()
    historical_data = get_historical_data()
    prediction_data = get_prediction_data()
    
    if sensor_data and historical_data is not None:
        # 현재 시간 표시
        st.markdown(
            f'<div class="time-display">조회 시간: {current_time.strftime("%Y-%m-%d %H:%M")}</div>',
            unsafe_allow_html=True
        )

        # 1. 내부 환경 데이터
        st.subheader('내부 환경', anchor=False)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                create_metric_card("내부 온도", f"{sensor_data['internal_temp']} °C"),
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                create_metric_card("내부 습도", f"{sensor_data['internal_humidity']} %"),
                unsafe_allow_html=True
            )

        # 2. 외부 환경 데이터
        st.subheader('외부 환경', anchor=False)
        cols = st.columns(4)
        
        metrics = [
            ("외부 온도", f"{sensor_data['external_temp']} °C"),
            ("풍향/풍속", f"{sensor_data['wind_direction']} {sensor_data['wind_speed']}m/s"),
            ("이슬점", f"{sensor_data['dew_point']} °C"),
            ("누적일사량", f"{sensor_data['solar_radiation']} J/cm²")
        ]
        
        for col, (label, value) in zip(cols, metrics):
            with col:
                st.markdown(
                    create_metric_card(label, value),
                    unsafe_allow_html=True
                )

        st.subheader('과거 30분 내부 환경 변화 및 예측', anchor=False)
        fig = create_combined_graph(historical_data, prediction_data)
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': False,
            'staticPlot': False,    #툴팁 (그래프 가져다대면 정보 나오게)
            'displaylogo': False,     # Plotly 로고 비활성화
            'scrollZoom': True,      # 스크롤로 줌 가능
        })
        
    time.sleep(1)
    st.rerun()

if __name__ == '__main__':
    main()