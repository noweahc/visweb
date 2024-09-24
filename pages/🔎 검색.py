import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tempfile
import matplotlib.font_manager as fm
import matplotlib as mpl
import platform
import os

# 폰트 등록 함수 - 캐시를 사용하여 폰트 목록 저장
@st.cache_data
def fontRegistered():
    font_dirs = [os.getcwd() + '/data/Nanum_Gothic']  # 폰트가 저장된 경로
    font_files = fm.findSystemFonts(fontpaths=font_dirs)

    for font_file in font_files:
        fm.fontManager.addfont(font_file)
    fm._load_fontmanager(try_read_cache=False)

def main():
    # 폰트 등록
    fontRegistered()

    # 등록된 폰트 목록 불러오기
    fontNames = [f.name for f in fm.fontManager.ttflist]
    selected_font = st.sidebar.selectbox("폰트를 선택하세요", fontNames)

    # 선택한 폰트로 설정
    plt.rc('font', family=selected_font)

    # CSV 파일을 읽어오는 부분
    df = pd.read_csv("data/finaldata.csv")

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

        num_frames = len(data['timestamp'].unique())
        ax.set_xlim(0, num_frames)

        numeric_max = data['count'].max()
        ax.set_ylim(0, numeric_max + 50)

        lines = {}
        colors = ['lightcoral', 'lightblue', 'lightgreen']
        labels = {}

        def update(frame):
            current_time = data['timestamp'].unique()[frame]
            current_data = data[data['timestamp'] <= current_time]

            top_3_current = current_data.groupby('person')['count'].last().nlargest(3).index

            for i, person in enumerate(top_3_current):
                person_data = current_data[current_data['person'] == person]
                if person not in lines:
                    lines[person], = ax.plot([], [], lw=4, label=person, color=colors[i % len(colors)])
                    labels[person] = ax.text(0, 0, person, fontsize=12, ha='right')

                x = list(range(len(person_data)))
                y = person_data['count'].values

                lines[person].set_data(x, y)
                labels[person].set_position((x[-1], y[-1]))
                labels[person].set_text(person[1:])

            if frame == num_frames - 1:
                top_3_current = current_data.groupby('person')['count'].last().nlargest(3)
                for rank, (person, count) in enumerate(top_3_current.items(), start=1):
                    ax.text(num_frames * 0.95, numeric_max - 15 * rank, 
                            f"{rank}위: {person}\n({count})", 
                            fontsize=18, ha='right', color='black')
                            
            ax.set_title(f"Time: {current_time}")
            return list(lines.values()) + list(labels.values())

        ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=900, blit=False, repeat=False)

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmpfile:
            ani.save(tmpfile.name, writer='pillow')
            return tmpfile.name

    # Streamlit 앱
    st.title(f"{selected_person}의 만남 애니메이션")

    # 애니메이션 생성 및 Streamlit에 표시
    gif_path = animate_race(result_df)
    st.image(gif_path)

if __name__ == "__main__":
    main()
