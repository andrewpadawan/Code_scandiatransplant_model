import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, box
import os
import re
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.patches import FancyArrowPatch
#from book_keeping.locations import CITY_COORDS_LAT_LONG

# Optional: real coordinates for Scandinavian cities
CITY_COORDS = {
    "Aarhus": (10.2039, 56.1629),
    "Copenhagen": (12.3, 55.6761),  # moved west so easier to see in plot
    "Odense": (10.4024, 55.4038),
    "Skane": (14, 56),     # moved east so easier to see in plot
    "Gothenburg": (11.9746, 57.7089),
    "Stockholm": (18.0686, 59.3293),
    "Uppsala": (17.6389, 59.8586),
    "Oslo": (10.7522, 59.9139),
    "Reykjavik": (-21.8954, 64.1355),
    "Helsinki": (24.9354, 60.1695),
    "Tartu": (26.7290, 58.3776)
}

CITY_COLORS = {
    "Aarhus": "#1f77b4",
    "Copenhagen": "#ff7f0e",
    "Odense": "#2ca02c",
    "Skane": "#d62728",
    "Gothenburg": "#9467bd",
    "Stockholm": "#8c564b",
    "Uppsala": "#e377c2",
    "Oslo": "#7f7f7f",
    "Reykjavik": "#bcbd22",
    "Helsinki": "#17becf",
    "Tartu": "#aec7e8"
}


SCANDINAVIA = ["Denmark", "Norway", "Sweden", "Finland", "Iceland"]

def load_europe_shapefile(shapefile_path):
    europe = gpd.read_file(shapefile_path)
    europe = europe.to_crs("EPSG:4326")  # Reproject to lon/lat
    europe = europe[europe['NAME'].isin(SCANDINAVIA)]
    bbox = box(-25, 54, 32, 68)
    europe['geometry'] = europe['geometry'].intersection(bbox)
    return europe

def plot_organ_flow_graph_on_map(csv_path, output_dir="logs/graph_images", shapefile_path= r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\book_keeping\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp", coords_dict= CITY_COORDS):

    df = pd.read_csv(csv_path)
    match = re.search(r"(matching_\d{8}_\d{6})", os.path.basename(csv_path))
    tag = match.group(1) if match else "graph"
    rad = 0.2
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"graph_{tag}.svg")

    edge_weights = (
        df.groupby(["DONOR_CITY", "RECIPIENT_CITY"])
          .size()
          .reset_index(name="NUM_TRANSFERS")
    )

    G = nx.DiGraph()
    for _, row in edge_weights.iterrows():
        src, dst, weight = row["DONOR_CITY"], row["RECIPIENT_CITY"], row["NUM_TRANSFERS"]
        G.add_edge(src, dst, weight=weight)

    base_map = load_europe_shapefile(shapefile_path)

    pos = {}
    fallback = nx.spring_layout(G, seed=42)
    for city in G.nodes:
        pos[city] = coords_dict.get(city, fallback[city])

    fig, ax = plt.subplots(figsize=(12, 10))
    base_map.plot(ax=ax, color='lightgray', edgecolor='black')

    node_colors = [CITY_COLORS.get(city, "lightblue") for city in G.nodes()]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=800)
    nx.draw_networkx_labels(G, pos, ax=ax)

    weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(weights) if weights else 1

    for u, v in G.edges():
        weight = G[u][v]['weight']
        scaled_weight = weight / max_weight if max_weight > 0 else 0
        color = plt.cm.viridis(scaled_weight)

        if u == v:
            # Draw self-loop with offset and curvature
            x, y = pos[u]
            dx, dy = 0.3, 0.3  # offset to simulate loop
            loop = FancyArrowPatch(
                (x, y), (x + dx, y + dy),
                connectionstyle="arc3,rad=7.0",
                arrowstyle='-|>',
                mutation_scale=30,
                lw=0.5 + 5 * scaled_weight,
                color=color
            )
            ax.add_patch(loop)
        else:
            nx.draw_networkx_edges(
                G, pos, ax=ax,
                edgelist=[(u, v)],
                arrowstyle='-|>',
                arrowsize=25,
                width=0.5 + 5 * scaled_weight,
                edge_color=[color],
                connectionstyle=f'arc3,rad={rad}'
            )

    norm = colors.Normalize(vmin=min(weights), vmax=max(weights))
    cmap = plt.cm.viridis  # ✅ lowercase fix
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("Number of Organ Transfers", fontsize=12)

    plt.title("Organ Flow Network Over Scandinavia")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

    return G



