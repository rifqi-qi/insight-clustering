import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import linear

def load_data():
    """Load data from GitHub URLs"""
    world_url = 'https://raw.githubusercontent.com/rifqi-qi/insight-clustering/refs/heads/main/world_map.geojson'
    clustered_data_url = 'https://raw.githubusercontent.com/rifqi-qi/insight-clustering/refs/heads/main/clustered_production_data.csv'
    
    world = gpd.read_file(world_url)
    clustered_df = pd.read_csv(clustered_data_url)
    return world, clustered_df

def create_interactive_map(world, clustered_df):
    """Create interactive map with Folium and color countries by cluster"""
    sea_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines',
                     'Singapore', 'Brunei', 'Cambodia', 'Laos', 'Myanmar']
    world['is_sea'] = world['NAME'].isin(sea_countries)
    sea_map = world.copy()

    sea_map = sea_map.merge(clustered_df[['Entity', 'Cluster', 'total_production', 'growth_rate']],
                            left_on='NAME', right_on='Entity', how='left')
    
    clusters = sea_map['Cluster'].dropna().unique()
    cluster_colormap = linear.Spectral_11.scale(min(clusters), max(clusters))
    cluster_colormap.caption = "Cluster Color Map"

    m = folium.Map(location=[5, 115], zoom_start=4, tiles="CartoDB positron")

    for _, row in sea_map.iterrows():
        color = (
            cluster_colormap(row['Cluster']) 
            if not pd.isna(row['Cluster']) 
            else "none"
        )
        tooltip_text = (
            f"<b>{row['NAME']}</b><br>"
            f"Cluster: {row['Cluster'] if not pd.isna(row['Cluster']) else 'N/A'}<br>"
            f"Total Production: {row['total_production'] if not pd.isna(row['total_production']) else 'N/A'}<br>"
            f"Growth Rate: {row['growth_rate']:.2f}%<br>"
        )
        folium.GeoJson(
            data=row['geometry'].__geo_interface__,
            style_function=lambda feature, color=color: {
                "fillColor": color if color != "none" else "white",
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.7 if color != "none" else 0.1,
            },
            tooltip=tooltip_text,
        ).add_to(m)
    
    m.add_child(cluster_colormap)

    legend_html = f"""
    <div style="
        position: fixed; 
        bottom: 50px; left: 50px; 
        z-index: 9999; 
        background-color: white; 
        padding: 10px; 
        border: 2px solid grey;
        font-size: 14px;">
        <b>Legenda Produksi:</b><br>
        <b>Cluster 0 (Produksi Tinggi):</b>
        <ul>
    """
    for _, row in clustered_df[clustered_df['Cluster'] == 0].iterrows():
        legend_html += f"<li>{row['Entity']}: {row['total_production']:,} ton</li>"
    
    legend_html += """
        </ul>
        <b>Cluster 1 (Produksi Rendah):</b>
        <ul>
    """
    for _, row in clustered_df[clustered_df['Cluster'] == 1].iterrows():
        legend_html += f"<li>{row['Entity']}: {row['total_production']:,} ton</li>"
    
    legend_html += """
        </ul>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    return m

def main():
    st.title('Southeast Asia Production Clustering Map')

    try:
        world, clustered_df = load_data()
        m = create_interactive_map(world, clustered_df)

        # Save map to HTML and display in Streamlit
        m.save("map_with_legend.html")
        with open("map_with_legend.html", "r", encoding="utf-8") as f:
            html = f.read()
        st.components.v1.html(html, height=700)
        
    except Exception as e:
        st.error(f"Error loading data: {e}")

if __name__ == '__main__':
    main()
