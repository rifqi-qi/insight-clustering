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
    
    world = gpd.read_file(world_url)
    clustered_df = pd.read_csv(clustered_data_url)
    return world, clustered_df

def create_interactive_map(world, clustered_df):
    """Create interactive map with Folium and color countries by cluster"""
    sea_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines',
                     'Singapore', 'Brunei', 'Cambodia', 'Laos', 'Myanmar']
    world['is_sea'] = world['NAME'].isin(sea_countries)
    sea_map = world.copy()

    sea_map = sea_map.merge(clustered_df[['Entity', 'Cluster', 'total_production', 'growth_rate', 'avg_annual_production']],
                            left_on='NAME', right_on='Entity', how='left')
    
    clusters = sea_map['Cluster'].dropna().unique()
    cluster_colormap = linear.Spectral_11.scale(min(clusters), max(clusters))
    cluster_colormap.caption = "Cluster Color Map"

    m = folium.Map(location=[5, 115], zoom_start=4, tiles="CartoDB positron", control_scale=True)

    Fullscreen().add_to(m)

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
        ).add_to(m)
    
    m.add_child(cluster_colormap)

    # Calculate high and low production countries
    high_production = clustered_df.nlargest(3, 'total_production')
    low_production = clustered_df.nsmallest(3, 'total_production')

    # Add custom legend for high/low production
    legend_html = f"""
    <div style="
        position: absolute; 
        top: 10px; left: 10px; width: 300px; height: auto; 
        z-index:9999; font-size:14px; background-color:white; 
        border:2px solid black; padding: 10px;">
    <h4 style="margin-bottom: 10px;">Keterangan Produksi</h4>
    <strong>Negara dengan Produksi Tertinggi:</strong>
    <ul style="margin: 5px 0; padding-left: 15px;">
        {''.join([f"<li>{row['Entity']}: {int(row['total_production']):,}</li>" for _, row in high_production.iterrows()])}
    </ul>
    <strong>Negara dengan Produksi Terendah:</strong>
    <ul style="margin: 5px 0; padding-left: 15px;">
        {''.join([f"<li>{row['Entity']}: {int(row['total_production']):,}</li>" for _, row in low_production.iterrows()])}
    </ul>
    </div>
    """
    # Add legend directly to Folium's map HTML
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

def main():
    st.set_page_config(layout="wide")  # Set Streamlit layout to wide
    st.title('Southeast Asia Production Clustering Map')

    try:
        world, clustered_df = load_data()
        m = create_interactive_map(world, clustered_df)
        from streamlit_folium import st_folium
        st_folium(m, width=1500, height=800)
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check the GitHub URLs and ensure files are accessible")

if __name__ == '__main__':
    main()
