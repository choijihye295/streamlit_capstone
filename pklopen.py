import pickle
import os

def load_lgb_models(directory):
    """
    디렉토리에서 LightGBM 모델 파일들을 읽어오는 함수
    """
    models = {}
    try:
        # 온도 모델 로드
        temp_path = os.path.join(directory, 'lgb_temp_model_1min.pkl')
        with open(temp_path, 'rb') as f:
            models['temperature'] = pickle.load(f)
            print("온도 모델 로드 완료")
            
        # 습도 모델 로드
        humid_path = os.path.join(directory, 'lgb_humid_model_1min.pkl')
        with open(humid_path, 'rb') as f:
            models['humidity'] = pickle.load(f)
            print("습도 모델 로드 완료")
            
        return models
    except Exception as e:
        print(f"모델 로드 중 오류 발생: {str(e)}")
        return None
def analyze_lgb_model(model, model_name):
    """
    LightGBM 모델의 기본 정보를 분석하는 함수
    """
    print(f"\n=== {model_name} 모델 분석 ===")
    print(f"모델 타입: {type(model)}")
    
    # LightGBM 모델의 속성 분석
    print("\n모델 속성:")
    for attr in dir(model):
        if not attr.startswith('_'):  # private 속성 제외
            try:
                value = getattr(model, attr)
                # 함수가 아닌 속성만 출력
                if not callable(value):
                    print(f"- {attr}: {value}")
            except Exception as e:
                print(f"  [에러 발생: {attr}] {str(e)}")

# 메인 실행 코드
if __name__ == "__main__":
    directory = "/Users/choejihye/pkl"
    models = load_lgb_models(directory)
    
    if models:
        for model_name, model in models.items():
            analyze_lgb_model(model, model_name)

