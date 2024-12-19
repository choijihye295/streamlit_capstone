import pandas as pd
import pickle
import time
from datetime import datetime, timedelta
import numpy as np
import os

def prepare_data_from_time(data, start_time):
    """특정 시간까지의 데이터만 사용"""
    data['저장시간'] = pd.to_datetime(data['저장시간'])
    return data[data['저장시간'] <= start_time].copy()

def predict_next_values(temp_model_dict, humid_model_dict, data):
    """다음 시점 예측"""
    try:
        # 입력 데이터 준비
        X = data[['내부온도', '내부습도']].iloc[-1:]
        
        # 스케일러 적용
        X_scaled_temp = temp_model_dict['scaler'].transform(X)
        X_scaled_humid = humid_model_dict['scaler'].transform(X)
        
        # 예측
        next_temp = temp_model_dict['model'].predict(X_scaled_temp)[0]
        next_humid = humid_model_dict['model'].predict(X_scaled_humid)[0]
        
        # 예측값이 너무 급격하게 변하지 않도록 제한
        last_temp = float(data['내부온도'].iloc[-1])
        last_humid = float(data['내부습도'].iloc[-1])
        
        # 변화량을 제한 (최대 ±0.5도, ±1% 변화)
        next_temp = last_temp + np.clip(next_temp - last_temp, -0.5, 0.5)
        next_humid = last_humid + np.clip(next_humid - last_humid, -1.0, 1.0)
        
        return float(next_temp), float(next_humid)
        
    except Exception as e:
        print(f"예측 중 오류 발생: {str(e)}")
        last_temp = float(data['내부온도'].iloc[-1])
        last_humid = float(data['내부습도'].iloc[-1])
        return (
            last_temp + np.random.uniform(-0.2, 0.2),
            last_humid + np.random.uniform(-0.3, 0.3)
        )

def save_prediction(next_time, next_temp, next_humid, mode='a'):
    """예측 데이터 저장 (누적)"""
    new_prediction = pd.DataFrame({
        '예측시간': [next_time],
        '예측온도': [round(next_temp, 1)],
        '예측습도': [round(next_humid, 1)]
    })

    if mode == 'w' or not os.path.exists("predictions.csv"):
        # 파일이 없거나 초기화 모드일 때는 새로 생성
        new_prediction.to_csv("predictions.csv", index=False)
    else:
        # 기존 파일이 있을 때는 누적
        predictions = pd.read_csv("predictions.csv")
        updated_predictions = pd.concat([predictions, new_prediction], ignore_index=True)
        updated_predictions.to_csv("predictions.csv", index=False)
    
    print(f"예측 완료 - 시간: {next_time}, 온도: {round(next_temp, 1)}°C, 습도: {round(next_humid, 1)}%")

def run_prediction_service():
    """예측 서비스 실행"""
    print("예측 서비스를 시작합니다...")
    
    # 모델 파일 경로
    temp_model_path = "/Users/choejihye/pkl/lgb_temp_model_1min.pkl"
    humid_model_path = "/Users/choejihye/pkl/lgb_humid_model_1min.pkl"
    
    # 시작 시간 설정
    start_time = pd.Timestamp('2018-05-10 09:50:00')
    print(f"예측 시작 시간: {start_time}")
    
    # 모델 로드
    try:
        with open(temp_model_path, 'rb') as f:
            temp_model_dict = pickle.load(f)
        with open(humid_model_path, 'rb') as f:
            humid_model_dict = pickle.load(f)
        print("모델 로드 완료")
    except Exception as e:
        print(f"모델 로드 실패: {str(e)}")
        return
    
    # 초기 데이터 읽기
    data = pd.read_csv("sensor_data.csv")
    data = prepare_data_from_time(data, start_time)
    current_time = start_time
    
    # predictions.csv 초기화
    if os.path.exists("predictions.csv"):
        os.remove("predictions.csv")
    
    while current_time < pd.Timestamp('2018-05-10 10:00:00'):
        try:
            # 예측
            next_temp, next_humid = predict_next_values(temp_model_dict, humid_model_dict, data)
            next_time = current_time + timedelta(minutes=1)
            
            # 예측 결과 저장 (누적)
            save_prediction(next_time, next_temp, next_humid)
            
            # 예측 결과를 데이터에 추가
            new_row = pd.DataFrame({
                '저장시간': [next_time],
                '내부온도': [round(next_temp, 1)],
                '내부습도': [round(next_humid, 1)]
            })
            data = pd.concat([data, new_row], ignore_index=True)
            
            # 시간 업데이트
            current_time = next_time
            
            # 1초 대기
            time.sleep(1)
            
        except Exception as e:
            print(f"에러 발생: {str(e)}")
            time.sleep(1)
    
    # 최종 결과 출력
    print("\n예측 완료")
    predictions = pd.read_csv("predictions.csv")
    print("\n최종 예측 결과:")
    print(predictions)

if __name__ == "__main__":
    run_prediction_service()