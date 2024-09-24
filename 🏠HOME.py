import streamlit as st
from PIL import Image


def show():
    # 사이드바 설정
    st.sidebar.title("About")
    
    # 링크 이모지를 사이드바에 추가 (크게 표시)
    st.sidebar.markdown("<h1 style='text-align: center; font-size: 100px;'>🌎</h1>", unsafe_allow_html=True)    
    # GitHub 링크 추가
    st.sidebar.markdown("**GitHub URL**")
    st.sidebar.write("[Visit our GitHub](https://github.com/Fintech2024-Team2/Visualization)")

    # 메인 페이지 내용
    st.title("🎈 Workshop Visualization Project")
    st.write("""
    환영합니다! 이 페이지는 워크숍에서 찍은 사진을 바탕으로 인물 간의 관계를 시각화한 프로젝트의 홈 화면입니다. 
    사이드바를 통해 원하는 메뉴를 선택할 수 있습니다. 
    """)

    # 메인 페이지 이미지 로드 및 표시
    image_path = "/Users/chaewon/Desktop/snukdt/시각화웹개발/project/Visualization/사진첩구현/체육대회/KakaoTalk_20240814_체육대회단체.jpg"
    img = Image.open(image_path)
    st.image(img, use_column_width=True)

if __name__ == "__main__":
    show()
