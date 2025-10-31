import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry import box



europe = gpd.read_file(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\book_keeping\ne_110m_admin_0_countries\ne_110m_admin_0_countries.shp")
scandinavia = ["Denmark", "Sweden", "Norway", "Finland", "Iceland", "Estonia"]
europe = europe[europe['NAME'].isin(scandinavia)]

bbox = box(-25, 54, 32, 68)   # Up to 66°N
europe_clipped = europe.copy()
europe_clipped['geometry'] = europe_clipped['geometry'].intersection(bbox)
#cities = gpd.read_file(r"C:\Users\reddr\OneDrive\Andrea\Master in Computer Science and Engineering\Thesis\Code\Scandiatransplant_modelling\book_keeping\ne_110m_populated_places\ne_110m_populated_places.shp")

#print(sorted(cities['NAME'].unique()))


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


# Convert to GeoDataFrame
manual_df = pd.DataFrame([
    {"NAME": name, "geometry": Point(lon, lat)}
    for name, (lat, lon) in CITY_COORDS.items()
])
manual_gdf = gpd.GeoDataFrame(manual_df, geometry="geometry", crs="EPSG:4326")


fig, ax = plt.subplots(figsize=(12, 10))

# Plot Europe map
europe_clipped.plot(ax=ax, color='lightgray', edgecolor='black')

# Plot manual cities
manual_gdf.plot(ax=ax, color='blue', markersize=50)

# Annotate city names
for _, row in manual_gdf.iterrows():
    ax.text(row.geometry.x + 0.3, row.geometry.y + 0.3, row['NAME'], fontsize=9)

plt.title("Scanditransplant members")
plt.tight_layout()
plt.show()














"""cities = cities[cities['NAME'].isin([
    "Stockholm", "Copenhagen", "Oslo", "Helsinki", "Reykjavik",
    "Aarhus", "Odense", "Malmö", "Uppsala", "Tartu"
])]"""

""" fig, ax = plt.subplots(figsize=(12, 10))
europe.plot(ax=ax, color='lightgray', edgecolor='black')  # Background map
cities.plot(ax=ax, color='blue', markersize=50)           # City points

# Annotate city names
for _, row in cities.iterrows():
    ax.text(row.geometry.x + 0.3, row.geometry.y + 0.3, row['NAME'], fontsize=9)

plt.title("Organ Flow Cities on European Map")
plt.tight_layout()
plt.show()
 """



""" CITY_COORDS = {
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


def load_matches(csv_path):
    df = pd.read_csv(csv_path)
    df = df[df['DONOR_CITY'].isin(CITY_COORDS) & df['RECIPIENT_CITY'].isin(CITY_COORDS)]
    df['donor_coords'] = df['DONOR_CITY'].map(CITY_COORDS)
    df['recipient_coords'] = df['RECIPIENT_CITY'].map(CITY_COORDS)
    return df


def plot_flows(df, title="Organ Allocation Flows"):
    # Load Europe map manually (replace deprecated call)
    europe = 
    europe = europe[europe['CONTINENT'] == 'Europe']

    fig, ax = plt.subplots(figsize=(12, 10))
    europe.plot(ax=ax, color='lightgray', edgecolor='black')

    # Plot organ flow arrows
    for _, row in df.iterrows():
        lat1, lon1 = row['donor_coords']
        lat2, lon2 = row['recipient_coords']
        ax.annotate("",
                    xy=(lon2, lat2), xycoords='data',
                    xytext=(lon1, lat1), textcoords='data',
                    arrowprops=dict(arrowstyle="->", color='red', lw=1.5),
                    )
    cities = gpd.read_file("book_keeping\\ne_110m_populated_places\\ne_110m_populated_places.shp")
    cities = cities[cities['NAME'].isin(["Stockholm", "Copenhagen", "Oslo", "Helsinki", "Reykjavik", "Aarhus", "Odense", "Malmö", "Uppsala", "Tartu" ])]
    # Plot cities from GeoDataFrame
    cities.plot(ax=ax, color='blue', markersize=30)
    for _, row in cities.iterrows():
        ax.text(row.geometry.x + 0.3, row.geometry.y + 0.3, row['NAME'], fontsize=9)

    plt.title(title)
    plt.tight_layout()
    plt.show() """