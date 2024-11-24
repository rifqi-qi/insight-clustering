import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
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
    """Create interactive map with Folium and color countries by cluster"""
    # Filter Southeast Asian countries
    sea_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines',
                     'Singapore', 'Brunei', 'Cambodia', 'Laos', 'Myanmar']
    world['is_sea'] = world['NAME'].isin(sea_countries)
    sea_map = world.copy()

    # Merge clustering data with map
    sea_map = sea_map.merge(clustered_df[['Entity', 'Cluster', 'total_production', 'growth_rate']],
                            left_on='NAME', right_on='Entity', how='left')
    
    # Define color map for clusters
    clusters = sea_map['Cluster'].dropna().unique()
    cluster_colormap = linear.Spectral_11.scale(min(clusters), max(clusters))
    cluster_colormap.caption = "Cluster Color Map"

    # Initialize Folium map
    m = folium.Map(location=[5, 115], zoom_start=4, tiles="CartoDB positron")

    # Add countries to map
    for _, row in sea_map.iterrows():
        # Countries with cluster are colored, others are default map color (no fill)
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
                "fillColor": color if color != "none" else "white",  # Fill white for no cluster
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.7 if color != "none" else 0.1,  # Transparent for no cluster
            },
            tooltip=tooltip_text,
        ).add_to(m)
    
    # Add color map legend
    m.add_child(cluster_colormap)

    return m

def main():
    st.title('Southeast Asia Production Clustering Map')

    # Use custom CSS to remove padding and make the map full width
    st.markdown("""
        <style>
            .streamlit-expanderHeader {
                font-size: 20px;
            }
            .main {
                padding-left: 0;
                padding-right: 0;
            }
            .block-container {
                padding-left: 0;
                padding-right: 0;
            }
            .streamlit-folium {
                width: 100%;
                height: 100vh;
            }
        </style>
    """, unsafe_allow_html=True)

    # Load data
    try:
        world, clustered_df = load_data()
        
        # Create map
        m = create_interactive_map(world, clustered_df)
        
        # Display map in Streamlit with full width and height
        from streamlit_folium import st_folium
        st_folium(m, width=800, height=600)
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check the GitHub URLs and ensure files are accessible")

if __name__ == '__main__':
    main()
