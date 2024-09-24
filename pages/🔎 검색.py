import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tempfile
import matplotlib.font_manager as fm
import matplotlib as mpl

# 한글 폰트 설정
font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"  # macOS의 한글 폰트 경로
font_prop = fm.FontProperties(fname=font_path)
mpl.rc('font', family=font_prop.get_name())

# CSV 파일을 읽어오는 부분
df = pd.read_csv("../../finaldata.csv")

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

# 애니메이션 생성 함수
def animate_race(data):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # x축 범위는 순위에 따라 설정
    num_frames = len(data['timestamp'].unique())
    ax.set_xlim(0, num_frames)

    # y축 범위는 누적 만남 횟수에 따라 설정
    numeric_max = data['count'].max()
    ax.set_ylim(0, numeric_max + 50)  # 여유를 주기 위해 y축 범위를 더 늘림

    # 라인 초기화
    lines = {}
    colors = ['lightcoral', 'lightblue', 'lightgreen']
    labels = {}

    def update(frame):
        current_time = data['timestamp'].unique()[frame]
        current_data = data[data['timestamp'] <= current_time]
        
        # 그때그때 상위 3명을 선택
        top_3_current = current_data.groupby('person')['count'].last().nlargest(3).index

        for i, person in enumerate(top_3_current):
            person_data = current_data[current_data['person'] == person]
            if person not in lines:
                lines[person], = ax.plot([], [], lw=4, label=person, color=colors[i % len(colors)])
                labels[person] = ax.text(0, 0, person, fontsize=12, ha='right')

            x = list(range(len(person_data)))
            y = person_data['count'].values + i * 5 + np.random.normal(0, 0.5, len(person_data))  # y축 위치에 변동 추가
            
            lines[person].set_data(x, y)
            
            # 이름을 그래프 끝에 표시
            labels[person].set_position((x[-1], y[-1]))
            labels[person].set_text(person[1:])  # 성을 제외한 이름 표시

        # 마지막 프레임에 상위 3명 팝업 텍스트 추가
        if frame == num_frames - 1:
            top_3_current = current_data.groupby('person')['count'].last().nlargest(3)
            for rank, (person, count) in enumerate(top_3_current.items(), start=1):
                ax.text(num_frames * 0.95, numeric_max - 15 * rank, 
                        f"{rank}위: {person}\n({count})", 
                        fontsize=18, ha='right', color='black')
                        
        ax.set_title(f"Time: {current_time}")
        return list(lines.values()) + list(labels.values())

    # 애니메이션 속도를 조절 (interval 값을 더 크게 설정하여 속도 느리게)
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
