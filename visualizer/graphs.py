import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, box
import os
import re
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

def plot_organ_flow_graph_on_map(csv_path, output_dir="graph_images", shapefile_path= r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\book_keeping\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp", coords_dict= CITY_COORDS):
    df = pd.read_csv(csv_path)
    # Extract timestamp tag from filename
    match = re.search(r"(matching_\d{8}_\d{6})", os.path.basename(csv_path))
    tag = match.group(1) if match else "graph"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"graph_{tag}.svg")
    
    # Count flows between cities
    edge_weights = (
        df.groupby(["DONOR_CITY", "RECIPIENT_CITY"])
          .size()
          .reset_index(name="NUM_TRANSFERS")
    )

    # Build directed graph
    G = nx.DiGraph()
    for _, row in edge_weights.iterrows():
        src, dst, weight = row["DONOR_CITY"], row["RECIPIENT_CITY"], row["NUM_TRANSFERS"]
        G.add_edge(src, dst, weight=weight)

    # Load and clip map
    base_map = load_europe_shapefile(shapefile_path)

    # Build position dict from coords
    pos = {}
    fallback = nx.spring_layout(G, seed=42)
    for city in G.nodes:
        if city in coords_dict:
            pos[city] = coords_dict[city]
        else:
            pos[city] = fallback[city]

    # Plot map
    fig, ax = plt.subplots(figsize=(12, 10))
    base_map.plot(ax=ax, color='lightgray', edgecolor='black')

    # Plot nodes and labels
    node_colors = [CITY_COLORS.get(city, "lightblue") for city in G.nodes()]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=800)


    nx.draw_networkx_labels(G, pos, ax=ax)

    # Plot edges with curvature
    weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(weights) if weights else 1

    for u, v in G.edges():
        weight = G[u][v]['weight']
        if G.has_edge(v, u) and u != v:
            rad = 0.2  # curve for bidirectional
        elif u == v:
            rad = 0.4  # self-loop
        else:
            rad = 0.0  # straight

        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=[(u, v)],
            arrowstyle='-|>',
            arrowsize=25,
            width=1.5 * weight,
            edge_color=plt.cm.Blues(weight / max_weight),
            connectionstyle=f'arc3,rad={rad}'
        )

    plt.title("Organ Flow Network Over Scandinavia")
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

    return G


plot_organ_flow_graph_on_map(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\csv_logs\matching_20251031_140724.csv")