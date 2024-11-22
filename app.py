import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium

def load_data():
    """Load data from GitHub URLs"""
    # Replace with your actual GitHub raw file URLs
    world_url = 'https://raw.githubusercontent.com/rifqi-qi/insight-clustering/refs/heads/main/world_map.geojson'
    clustered_data_url = 'https://raw.githubusercontent.com/rifqi-qi/insight-clustering/refs/heads/main/clustered_production_data.csv'
    
    # Load world map
    world = gpd.read_file(world_url)
    
    # Load clustered data
    clustered_df = pd.read_csv(clustered_data_url)
    
    return world, clustered_df

def create_interactive_map(world, clustered_df):
    """Create an interactive map using folium"""
    # Filter Southeast Asian countries
    sea_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines',
                     'Singapore', 'Brunei', 'Cambodia', 'Laos', 'Myanmar']
    sea_map = world[world['NAME'].isin(sea_countries)]

    # Merge clustering data with map
    sea_map = sea_map.merge(clustered_df[['Entity', 'Cluster', 'total_production', 'growth_rate']],
                            left_on='NAME', right_on='Entity', how='left')

    # Create Folium map centered on Southeast Asia
    m = folium.Map(location=[10, 105], zoom_start=4, tiles='cartodbpositron')

    # Add countries with clusters
    for _, row in sea_map.iterrows():
        color = {0: 'blue', 1: 'green'}.get(row['Cluster'], 'gray')  # Color by cluster
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, color=color: {'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.6},
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'Cluster', 'total_production', 'growth_rate'],
                aliases=['Country', 'Cluster', 'Total Production', 'Growth Rate (%)'],
                localize=True
            )
        ).add_to(m)

    return m

def main():
    st.title('Interactive Southeast Asia Production Clustering Map')
    
    # Load data
    try:
        world, clustered_df = load_data()
        
        # Create map
        folium_map = create_interactive_map(world, clustered_df)
        
        # Display map in Streamlit
        st_folium(folium_map, width=800, height=600)
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check the GitHub URLs and ensure files are accessible")

if __name__ == '__main__':
    main()
