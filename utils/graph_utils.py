import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from .image_utils import rotate_image_by_exif
import os
from PIL import Image, ExifTags


def create_graph(time_point, df):
    G = nx.Graph()
    sub_df = df[df['timestamp'] <= time_point]
    for filename, group in sub_df.groupby('filename'):
        persons = list(group['class'])
        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                if G.has_edge(persons[i], persons[j]):
                    G[persons[i]][persons[j]]['weight'] += 1
                else:
                    G.add_edge(persons[i], persons[j], weight=1)
    pos = nx.spring_layout(G)
    return G, pos, sub_df

def plot_graph(G, pos, sub_df, font_prop):
    fig, ax = plt.subplots(figsize=(10, 7))
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    nx.draw(G, pos, ax=ax, with_labels=False, width=weights, node_color='lightblue', edge_color='gray')
    for node, (x, y) in pos.items():
        row = sub_df[sub_df['class'] == node].iloc[0]
        img_file = row['filename']
        img_path = os.path.join('/Users/chaewon/Desktop/snukdt/시각화웹개발/project/image', img_file)
        
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img = rotate_image_by_exif(img)
            bbox = (row['xmin'], row['ymin'], row['xmax'], row['ymax'])
            add_image_to_node(node, (x, y), ax, img, bbox, font_prop, zoom=0.2)  # 여기에 font_prop 추가
        else:
            ax.text(x, y, s=node, bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'),
                    horizontalalignment='center', fontproperties=font_prop, fontsize=12, fontweight='bold')
    return fig



def add_image_to_node(node, pos, ax, img, bbox, font_prop, zoom=0.2):
    xmin, ymin, xmax, ymax = bbox
    face = img.crop((xmin, ymin, xmax, ymax))
    imagebox = OffsetImage(face, zoom=zoom)
    ab = AnnotationBbox(imagebox, pos, frameon=False)
    ax.add_artist(ab)
    ax.text(pos[0], pos[1] - 0.2, node, ha='center', fontproperties=font_prop, fontsize=12, fontweight='bold')
