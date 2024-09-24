import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tempfile
import matplotlib.font_manager as fm
import matplotlib as mpl
import platform

# 한글 폰트 설정
font_path = "data/Nanum_Gothic/NanumGothic-Regular.ttf"  # 폰트 경로
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# CSV 파일을 읽어오는 부분
df = pd.read_csv("data/finaldata.csv")

# '0번' 인물 제거
df = df[df['class'] != 0]

# 시간 데이터를 datetime 형식으로 변환
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Streamlit 사이드바에서 인물 선택 UI 추가
nodes = df['class'].unique()
selected_person = st.sidebar.selectbox("인물을 선택하세요", nodes)

# 선택된 인물과 다른 인물들이 얼마나 자주 만났는지 계산
result = []

for timestamp, group in df.groupby('timestamp'):
    if selected_person in group['class'].values:
        relation_counts = {}
        for person in group['class'].unique():
            if person != selected_person:
                count = group[(group['class'] == selected_person) & (group['filename'].isin(group[group['class'] == person]['filename']))].shape[0]
                relation_counts[person] = relation_counts.get(person, 0) + count

        # 결과 저장
        for person, count in relation_counts.items():
            result.append({"timestamp": timestamp, "person": person, "count": count})

# DataFrame으로 변환
result_df = pd.DataFrame(result)

# 누적 합 계산 (시간에 따른 누적 만남 횟수)
result_df = result_df.groupby(["timestamp", "person"]).sum().groupby('person').cumsum().reset_index()

# 애니메이션 생성 함수 - 상위 5명만 표시
def animate_race(data):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    num_frames = len(data['timestamp'].unique())
    ax.set_xlim(0, num_frames)
    
    # 출발점 다르게 설정
    ax.set_ylim(0, 6)  # 상위 5명 + 여유 공간

    # 라인 초기화
    lines = {}
    labels = {}
    colors = ['lightcoral', 'lightblue', 'lightgreen', 'orange', 'purple']
    person_y_positions = {i: i + 1 for i in range(5)}  # 상위 5명을 위한 y축 위치 설정

    # 실시간 라벨 업데이트 함수
    def update(frame):
        # 현재 시간을 기반으로 데이터를 필터링
        current_time = data['timestamp'].unique()[frame]
        current_data = data[data['timestamp'] <= current_time]

        # 상위 5명을 가져오기
        top_5_current = current_data.groupby('person')['count'].last().nlargest(5).index

        # 기존 라벨 삭제
        for label in labels.values():
            label.remove()

        labels.clear()

        for i, person in enumerate(top_5_current):
            person_data = current_data[current_data['person'] == person]
            if person not in lines:
                lines[person], = ax.plot([], [], lw=4, label=person, color=colors[i % len(colors)])

            # x축 값과 y축 값 설정
            x = list(range(len(person_data)))
            y = [person_y_positions[i]] * len(person_data)  # y값을 상위 5명에 대해 다르게 설정
            
            # 그래프 업데이트
            lines[person].set_data(x, y)

            # 이름을 그래프 끝에 표시 (이전 이름 삭제 후 새로운 이름 추가)
            if len(x) > 0:
                labels[person] = ax.text(x[-1], y[-1], person, fontsize=12, ha='right')

        ax.set_title(f"Time: {current_time}")
        return list(lines.values()) + list(labels.values())

    # 애니메이션 속도 조절
    ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=900, blit=False, repeat=False)

    # 애니메이션을 GIF로 저장
    with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmpfile:
        ani.save(tmpfile.name, writer='pillow')
        return tmpfile.name

# Streamlit 앱
st.title(f"{selected_person}의 만남 애니메이션")

# 애니메이션 생성 및 Streamlit에 표시
gif_path = animate_race(result_df)
st.image(gif_path)
