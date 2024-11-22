import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from branca.colormap import linear

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
    """Create interactive map with Folium"""
    # Filter Southeast Asian countries
    sea_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines',
                     'Singapore', 'Brunei', 'Cambodia', 'Laos', 'Myanmar']
    world['is_sea'] = world['NAME'].isin(sea_countries)
    sea_map = world.copy()

    # Merge clustering data with map
    sea_map = sea_map.merge(clustered_df[['Entity', 'Cluster', 'total_production', 'growth_rate']],
                            left_on='NAME', right_on='Entity', how='left')
    
    # Initialize Folium map
    m = folium.Map(location=[5, 115], zoom_start=4, tiles="CartoDB positron")

    # Add countries to map
    for _, row in sea_map.iterrows():
        color = "lightgray" if pd.isna(row['Cluster']) else linear.Spectral_11.colors[int(row['Cluster'])]
        tooltip_text = (
            f"<b>{row['NAME']}</b><br>"
            f"Cluster: {row['Cluster'] if not pd.isna(row['Cluster']) else 'N/A'}<br>"
            f"Total Production: {row['total_production'] if not pd.isna(row['total_production']) else 'N/A'}<br>"
            f"Growth Rate: {row['growth_rate']:.2f}%<br>"
        )
        folium.GeoJson(
            data=row['geometry'].__geo_interface__,
            style_function=lambda _: {
                "fillColor": color,
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.7 if not pd.isna(row['Cluster']) else 0.2,
            },
            tooltip=tooltip_text,
        ).add_to(m)
    
    return m

def main():
    st.title('Southeast Asia Production Clustering Map')

    # Load data
    try:
        world, clustered_df = load_data()
        
        # Create map
        m = create_interactive_map(world, clustered_df)
        
        # Display map in Streamlit
        from streamlit_folium import st_folium
        st_folium(m, width=800, height=600)
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check the GitHub URLs and ensure files are accessible")

if __name__ == '__main__':
    main()
