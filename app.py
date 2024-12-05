import streamlit as st
import pandas as pd
import numpy as np

def main():
    st.title('내 Streamlit 대시보드')
    
    # 데이터 생성 및 시각화
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['데이터1', '데이터2', '데이터3']
    )
    
    st.line_chart(chart_data)

if __name__ == '__main__':
    main()