import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from shapely.geometry import Point, box
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from matplotlib import gridspec
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.widgets import Button, Slider
from matplotlib import colormaps
import numpy as np
from collections import defaultdict
#from book_keeping.locations import CITY_COORDS_LONG_LAT

# Static city coordinates
CITY_COORDS = {
    "Aarhus": (56.1629, 10.2039),
    "Copenhagen": (55.6761, 12.5683),
    "Odense": (55.4038, 10.4024),
    "Skane": (55.604981, 13.003822),
    "Gothenburg": (57.7089, 11.9746),
    "Stockholm": (59.3293, 18.0686),
    "Uppsala": (59.8586, 17.6389),
    "Oslo": (59.9139, 10.7522),
    "Reykjavik": (64.1355, -21.8954),
    "Helsinki": (60.1695, 24.9354),
    "Tartu": (58.3776, 26.7290)
}

def normalize_organ(name):
    name = name.strip().lower()
    if name in ['kd', 'kidney']:
        return 'Kidney'
    elif name in ['lv', 'liver']:
        return 'Liver'
    elif name in ['ht', 'heart']:
        return 'Heart'
    # Add more mappings as needed
    return name.capitalize()


SCANDINAVIA = ["Denmark", "Sweden", "Norway", "Finland", "Iceland", "Estonia"]

def haversine_km(coord1, coord2):
    R = 6371
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def compute_frame_counts(flows, max_frames=40):
    distances = []
    for _, row in flows.iterrows():
        donor = CITY_COORDS.get(row['DONOR_CITY'])
        recipient = CITY_COORDS.get(row['RECIPIENT_CITY'])
        if donor and recipient:
            dist = haversine_km(donor, recipient)
            distances.append(dist)
        else:
            distances.append(0)
    max_dist = max(distances)
    frame_counts = [max(2, int(max_frames * (d / max_dist))) for d in distances]
    return frame_counts

def interpolate_path(start, end, steps=50):
    lat1, lon1 = start
    lat2, lon2 = end
    lats = np.linspace(lat1, lat2, steps)
    lons = np.linspace(lon1, lon2, steps)
    return list(zip(lats, lons))

def build_synchronized_paths(flows, steps_per_timestep=25, delay_per_duplicate=10):
    all_paths = []
    route_counts = {}

    for row in flows.itertuples():
      
        donor = CITY_COORDS.get(row.DONOR_CITY)

        recipient = CITY_COORDS.get(row.RECIPIENT_CITY)
        
        if donor and recipient:
            route_key = (row.DONOR_CITY, row.RECIPIENT_CITY)
            count = route_counts.get(route_key, 0)
            route_counts[route_key] = count + 1

            delay = count * delay_per_duplicate
            path = interpolate_path(donor, recipient, steps_per_timestep)

            # Pad with donor location to simulate delay
            if delay > 0:
                pad = [donor] * delay
                path = pad + path

            # Ensure all paths are same length
            total_length = steps_per_timestep + delay_per_duplicate * (route_counts[route_key] - 1)
            path += [recipient] * (total_length - len(path))
            all_paths.append(path)

    return all_paths


def flatten_paths(paths):
    return [pt for path in paths for pt in path]

def load_europe_shapefile(shapefile_path):
    europe = gpd.read_file(shapefile_path)
    europe = europe[europe['NAME'].isin(SCANDINAVIA)]
    bbox = box(-25, 54, 32, 68)
    europe['geometry'] = europe['geometry'].intersection(bbox)
    return europe

def create_city_geodataframe():
    df = pd.DataFrame([
        {"NAME": name, "geometry": Point(lon, lat)}
        for name, (lat, lon) in CITY_COORDS.items()
    ])
    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

def animate_organ_flows(csv_path, shapefile_path):
    

    def normalize_organ(name):
        name = name.strip().lower()
        if name in ['kd', 'kidney']:
            return 'Kidney'
        elif name in ['lv', 'liver']:
            return 'Liver'
        elif name in ['ht', 'heart']:
            return 'Heart'
        return name.capitalize()

    organ_flows = pd.read_csv(csv_path).sort_values("TIMESTEP")
    europe_clipped = load_europe_shapefile(shapefile_path)
    manual_gdf = create_city_geodataframe()

    grouped = organ_flows.groupby("TIMESTEP")
    timestep_paths, timestep_labels, flow_counts, flow_metadata = [], [], [], []

    for ts, group in grouped:
        paths = build_synchronized_paths(group, steps_per_timestep=10)
        timestep_paths.append(paths)
        timestep_labels.append(ts)
        flow_counts.append(len(paths))
        flow_metadata.append(group.reset_index(drop=True))

    frames = []
    frame_timestep_indices = []
    color_maps = []
    for count in flow_counts:
        cmap = colormaps.get_cmap('tab20').resampled(count)
        color_maps.append([cmap(i) for i in range(count)])

    for i, paths in enumerate(timestep_paths):
        max_len = max(len(p) for p in paths)
        for step in range(max_len):
            frame_points = [path[step] if step < len(path) else path[-1] for path in paths]
            frames.append(frame_points)
            frame_timestep_indices.append(i)

    # Precompute cumulative organ tables per frame
    precomputed_tables = []
    cumulative_arrivals = defaultdict(lambda: defaultdict(int))
    cumulative_departures = defaultdict(lambda: defaultdict(int))
    seen_flows = set()

    for frame_idx in range(len(frames)):
        current_timestep = frame_timestep_indices[frame_idx]
        offset = sum(flow_counts[:current_timestep])
        paths = timestep_paths[current_timestep]
        meta = flow_metadata[current_timestep]
        new_arrival_cities = set()

        for j, path in enumerate(paths):
            global_index = offset + j
            if global_index in seen_flows:
                continue
            if global_index not in seen_flows:
                seen_flows.add(global_index)
                row = meta.iloc[j]
                organ = normalize_organ(row.DONOR_GRAFT_TYPE)
                cumulative_arrivals[organ][row.RECIPIENT_CITY] += 1
                cumulative_departures[organ][row.DONOR_CITY] += 1
                new_arrival_cities.add(row.RECIPIENT_CITY)

        organ_tables = {}
        organ_types = sorted(set(cumulative_arrivals.keys()) | set(cumulative_departures.keys()))
        for organ in organ_types:
            arrivals = cumulative_arrivals[organ]
            departures = cumulative_departures[organ]
            cities = sorted(set(arrivals.keys()) | set(departures.keys()))
            rows = []
            highlights = set()
            for city in cities:
                arr = arrivals.get(city, 0)
                dep = departures.get(city, 0)
                rows.append([city, arr, dep])
                if city in new_arrival_cities:
                    highlights.add(city)
            organ_tables[organ] = {"rows": rows, "highlights": highlights}

        precomputed_tables.append(organ_tables)

    # Set up figure
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(4, 2, height_ratios=[10, 1, 0.5, 0.5], width_ratios=[3, 1])
    ax = fig.add_subplot(gs[0, 0])
    progress_ax = fig.add_subplot(gs[1, 0])
    slider_ax = fig.add_subplot(gs[2, 0])
    button_ax = fig.add_subplot(gs[3, 0])
    table_ax = fig.add_subplot(gs[0, 1])
    table_ax.axis('off')

    europe_clipped.plot(ax=ax, color='lightgray', edgecolor='black')
    manual_gdf.plot(ax=ax, marker='^', facecolor='none', edgecolor='black', markersize=80)
    for _, row in manual_gdf.iterrows():
        name, x, y = row['NAME'], row.geometry.x, row.geometry.y
        dx, dy = (-0.2, 0.1) if name == 'Copenhagen' else (-0.5, -0.5) if name == 'Skane' else (-0.3, 0.1) if name == 'Odense' else (0.1, 0.1)
        ax.text(x + dx, y + dy, name, fontsize=9, ha='left', va='bottom')

    progress_bar, = progress_ax.plot([], [], color='green', lw=4)
    progress_ax.set_xlim(0, len(frames))
    progress_ax.set_ylim(0, 1)
    progress_ax.axis('off')
    title_text = fig.suptitle("", fontsize=16, color='darkred')

    slider = Slider(slider_ax, 'Frame', 0, len(frames) - 1, valinit=0, valstep=1)
    button = Button(button_ax, 'Pause', color='lightgray', hovercolor='lightblue')
    is_playing, current_frame, is_updating_slider, last_timestep = [True], [0], [False], [-1]
    points = []
    organ_axes = {}

    button.on_clicked(lambda event: toggle_play())
    def toggle_play():
        is_playing[0] = not is_playing[0]
        button.label.set_text('Play' if not is_playing[0] else 'Pause')

    def update(frame):
        current_timestep = frame_timestep_indices[frame]
        if current_timestep != last_timestep[0]:
            last_timestep[0] = current_timestep
            for pt in points:
                pt.remove()
            points.clear()
            for color in color_maps[current_timestep]:
                pt = ax.plot([], [], marker='o', markersize=8, color=color)[0]
                points.append(pt)

        for pt, (lat, lon) in zip(points, frames[frame]):
            pt.set_data([lon], [lat])
        progress_bar.set_data([0, frame], [0.5, 0.5])
        title_text.set_text(f"Organ Flow Animation — TIMESTEP: {timestep_labels[current_timestep]}")
        is_updating_slider[0] = True
        slider.set_val(frame)
        is_updating_slider[0] = False

        table_ax.clear()
        table_ax.axis('off')
        table_ax.set_title("Cumulative Organ Flow Summary", fontsize=12, weight='bold')

        organ_tables = precomputed_tables[frame]
        for idx, (organ, data) in enumerate(organ_tables.items()):
            rows = data["rows"]
            highlights = data["highlights"]
            cell_colors = [['#ccffcc' if row[0] in highlights else 'white'] * 3 for row in rows]

            if organ not in organ_axes:
                organ_axes[organ] = fig.add_axes([0.75, 0.3, 0.23, 0.6])

                organ_axes[organ].axis('off')

            sub_ax = organ_axes[organ]
            sub_ax.clear()
            sub_ax.axis('off')
            sub_ax.set_title(f"{organ}", fontsize=10, weight='bold')
            table = sub_ax.table(
                cellText=rows,
                colLabels=["City", "Arrived", "Departed"],
                cellColours=cell_colors,
                loc='center',
                cellLoc='left',
                colWidths=[0.3, 0.2, 0.2]
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.2)
            for key, cell in table.get_celld().items():
                if key[0] == 0:
                    cell.set_text_props(weight='bold')

        return points + [progress_bar, title_text]

    def manual_update(val):
        if not is_updating_slider[0]:
            current_frame[0] = int(val)
            update(current_frame[0])

    slider.on_changed(manual_update)

    def advance_frame():
        if is_playing[0]:
            current_frame[0] += 1
            if current_frame[0] < len(frames):
                update(current_frame[0])
            else:
                timer.stop()



    timer = fig.canvas.new_timer(interval=10)
    timer.add_callback(advance_frame)
    timer.start()

    update(0)
    plt.tight_layout()
    plt.show()





