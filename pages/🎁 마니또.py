import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from PIL import Image
import time

# Function to create the full network graph and positions
def create_full_network_graph(df):
    G = nx.DiGraph()
    for idx, row in df.iterrows():
        src = row['from']
        dst = row['to']
        description = row['description']
        G.add_edge(src, dst, description=description)
    pos = nx.spring_layout(G, seed=42)  # Fix the seed for consistent layout
    return G, pos

# Function to create subgraph based on current index
def create_subgraph(G, df, end_index):
    edges = [(row['from'], row['to']) for idx, row in df.iloc[:end_index+1].iterrows()]
    G_sub = G.edge_subgraph(edges).copy()
    return G_sub

# Function to plot the graph using Plotly
def plot_graph(G, pos):
    # Create edge traces for each edge
    edge_traces = []
    for edge in G.edges(data=True):
        src, dst, data = edge
        x0, y0 = pos[src]
        x1, y1 = pos[dst]

        edge_trace = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            line=dict(width=2, color='gray'),
            hoverinfo='none',
            mode='lines'
        )
        edge_traces.append(edge_trace)

    # Create node traces with hover text
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_hover_text = [f"<b>{node}</b><br>{G.nodes[node]['description']}" if 'description' in G.nodes[node] else f"<b>{node}</b>" for node in G.nodes()]
    node_text = [node for node in G.nodes()]  # 노드 이름만 표시

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        text=node_text,
        mode='markers+text',
        textposition="top center",
        hoverinfo='text',
        hovertext=node_hover_text,
        marker=dict(
            size=20,
            color='lightblue',
            line=dict(width=2, color='DarkSlateGrey')
        ),
        hoverlabel=dict(
            bgcolor="white",  # 말풍선 배경색
            font_size=16,  # 말풍선 글씨 크기
            font_family="Arial"  # 말풍선 글씨체
        )
    )

    # Combine all traces
    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        title_text="마니또 관계 그래프",
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20),
        height=700,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

# Streamlit app
def show():
    st.title("마니또 관계 시각화")
    st.write("시간에 따라 변하는 마니또 관계를 확인하세요.")
    
    # Load data
    df = pd.read_csv('/Users/chaewon/Desktop/manito.csv')
    
    # Initialize full graph and positions
    if 'full_G' not in st.session_state or 'pos' not in st.session_state:
        full_G, pos = create_full_network_graph(df)
        st.session_state['full_G'] = full_G
        st.session_state['pos'] = pos
    else:
        full_G = st.session_state['full_G']
        pos = st.session_state['pos']
    
    max_index = len(df) - 1
    current_index = st.slider("순서", 0, max_index + 1, 0, help="슬라이더를 움직여 시간에 따른 변화를 확인하세요.")
    
    # If current_index is 0, do not show the graph and data
    if current_index > 0:
        # Create subgraph based on current index
        G_sub = create_subgraph(full_G, df, current_index - 1)
        
        # Add node descriptions to G_sub
        for node in G_sub.nodes():
            G_sub.nodes[node]['description'] = df[df['from'] == node]['description'].values[0] if not df[df['from'] == node].empty else ""
        
        # Plot graph
        fig = plot_graph(G_sub, pos)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display data
        st.write("현재까지의 마니또 데이터:")
        st.dataframe(df.iloc[:current_index], height=600)

if __name__ == '__main__':
    show()
