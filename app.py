import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import linear
from folium.plugins import Fullscreen

def load_data():
    """Load data from GitHub URLs"""
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
    sea_map = sea_map.merge(clustered_df[['Entity', 'Cluster', 'total_production', 'growth_rate', 'avg_annual_production']],
                            left_on='NAME', right_on='Entity', how='left')
    
    # Define color map for clusters
    clusters = sea_map['Cluster'].dropna().unique()
    cluster_colormap = linear.Spectral_11.scale(min(clusters), max(clusters))
    cluster_colormap.caption = "Cluster Color Map"

    # Initialize Folium map
    m = folium.Map(location=[5, 115], zoom_start=4, tiles="CartoDB positron", control_scale=True)

    # Add fullscreen control
    Fullscreen().add_to(m)

    # Add countries to map
    for _, row in sea_map.iterrows():
        color = (
            cluster_colormap(row['Cluster']) 
            if not pd.isna(row['Cluster']) 
            else "none"
        )
        tooltip_text = (
            f"<b>{row['NAME']}</b><br>"
            f"Cluster: {int(row['Cluster']) if not pd.isna(row['Cluster']) else 'N/A'}<br>"
            f"Total Production: {f'{int(row['total_production']):,}' if not pd.isna(row['total_production']) else 'N/A'}<br>"
            f"Avg Annual Production: {f'{int(row['avg_annual_production']):,}' if not pd.isna(row['avg_annual_production']) else 'N/A'}<br>"
            f"Growth Rate: {f'{row['growth_rate']:.2f}%' if not pd.isna(row['growth_rate']) else 'N/A'}<br>"
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
            popup=folium.Popup(
                f"""
                <b>{row['NAME']}</b><br>
                Cluster: {int(row['Cluster']) if not pd.isna(row['Cluster']) else 'N/A'}<br>
                Total Production: {f'{int(row['total_production']):,}' if not pd.isna(row['total_production']) else 'N/A'}<br>
                Avg Annual Production: {f'{int(row['avg_annual_production']):,}' if not pd.isna(row['avg_annual_production']) else 'N/A'}<br>
                Growth Rate: {f'{row['growth_rate']:.2f}%' if not pd.isna(row['growth_rate']) else 'N/A'}
                """,
                max_width=250
            )
        ).add_to(m)
    
    # Add color map legend
    m.add_child(cluster_colormap)

    return m

def main():
    st.set_page_config(layout="wide")  # Set Streamlit layout to wide
    st.title('Southeast Asia Production Clustering Map')

    # Load data
    try:
        world, clustered_df = load_data()
        
        # Create map
        m = create_interactive_map(world, clustered_df)
        
        # Display map in Streamlit
        from streamlit_folium import st_folium
        output = st_folium(m, width=1500, height=600)  # Set large map size
        
        # Display country details below the map
        st.subheader("Country Details")
        if output["last_active_drawing"]:
            country_name = output["last_active_drawing"]["properties"]["NAME"]
            country_data = clustered_df[clustered_df['Entity'] == country_name]
            
            if not country_data.empty:
                st.markdown(f"**Country:** {country_name}")
                st.markdown(f"**Cluster:** {int(country_data['Cluster'].values[0])}")
                st.markdown(f"**Total Production:** {int(country_data['total_production'].values[0]):,}")
                st.markdown(f"**Avg Annual Production:** {int(country_data['avg_annual_production'].values[0]):,}")
                st.markdown(f"**Growth Rate:** {country_data['growth_rate'].values[0]:.2f}%")
            else:
                st.markdown(f"**Country:** {country_name}")
                st.markdown("**Cluster:** N/A")
                st.markdown("**Total Production:** N/A")
                st.markdown("**Avg Annual Production:** N/A")
                st.markdown("**Growth Rate:** N/A")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check the GitHub URLs and ensure files are accessible")

if __name__ == '__main__':
    main()
