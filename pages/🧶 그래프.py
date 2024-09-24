import streamlit as st
import pandas as pd
import os
import networkx as nx
import plotly.graph_objs as go
from utils.graph_utils import create_graph

# 데이터 로드
df = pd.read_csv('finaldata.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

def plot_graph_plotly(G, pos, node_data):
    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        edge_trace = go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=edge[2]['weight'], color='#888'),  # 엣지의 굵기를 개별적으로 설정
            hoverinfo='none',
            mode='lines'
        )
        edge_traces.append(edge_trace)

    node_x = []
    node_y = []
    node_color = []
    node_text = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_color.append('lightblue')  # 노드 색상 설정
        node_name = node[1:]  # 첫 글자를 제외한 이름으로 설정
        node_text.append(node_name)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color=node_color,
            size=20,  # 노드 크기 고정
            line=dict(width=2, color='DarkSlateGrey')
        ),
        text=node_text,
        textposition="middle center"  # 텍스트 위치를 노드 중앙에 설정
    )

    fig = go.Figure(data=edge_traces + [node_trace],
                    layout=go.Layout(
                        title='워크샵 인물 관계 그래프',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0,l=0,r=0,t=0),
                        annotations=[dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper"
                        )],
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False))
                    )
    return fig

def show():
    st.title("9기의 워크샵 인물 관계 그래프 시각화")

    time_point = st.slider(
        '시간 선택',
        min_value=df['timestamp'].min().to_pydatetime(),
        max_value=df['timestamp'].max().to_pydatetime(),
        value=df['timestamp'].min().to_pydatetime(),
        format="YYYY-MM-DD HH:mm:ss"
    )

    G, pos, sub_df = create_graph(time_point, df)
    fig = plot_graph_plotly(G, pos, sub_df)

    st.plotly_chart(fig)
if __name__ == "__main__":
    show()
