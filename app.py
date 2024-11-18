import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib_scalebar.scalebar import ScaleBar

def load_data():
    """Load data from GitHub URLs"""
    # Replace with your actual GitHub raw file URLs
    world_url = 'https://raw.githubusercontent.com/rifqi-qi/insight-clustering/refs/heads/main/ne_110m_admin_0_countries.shp'
    clustered_data_url = 'https://raw.githubusercontent.com/rifqi-qi/insight-clustering/refs/heads/main/clustered_production_data.csv'
    
    # Load world map
    world = gpd.read_file(world_url)
    
    # Load clustered data
    clustered_df = pd.read_csv(clustered_data_url)
    
    return world, clustered_df

def create_sea_map(world, clustered_df):
    """Create Southeast Asia production clustering map"""
    # Filter Southeast Asian countries
    sea_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines',
                     'Singapore', 'Brunei', 'Cambodia', 'Laos', 'Myanmar']
    sea_map = world[world['NAME'].isin(sea_countries)]

    # Merge clustering data with map
    sea_map = sea_map.merge(clustered_df[['Entity', 'Cluster', 'total_production', 'growth_rate']],
                            left_on='NAME', right_on='Entity', how='left')

    # Reproject to EPSG:3395 for centroid accuracy
    sea_map = sea_map.to_crs(epsg=3395)
    centroids = sea_map.geometry.centroid

    # Create plot
    fig, ax = plt.subplots(1, 1, figsize=(14, 10), constrained_layout=True)

    # Add divider for legend
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)

    # Plot map with boundaries and clusters
    sea_map.boundary.plot(ax=ax, linewidth=0, edgecolor="black")
    sea_map.plot(column='Cluster', ax=ax, legend=True, cmap='Spectral', 
                 edgecolor='darkgray', legend_kwds={'shrink': 0.8}, cax=cax)

    # Annotation texts
    texts = []
    for centroid, label, total_prod, growth_rate, cluster in zip(
        centroids, sea_map['NAME'], sea_map['total_production'], 
        sea_map['growth_rate'], sea_map['Cluster']
    ):
        x, y = centroid.x, centroid.y
        annotation_text = (f"{label}\nCluster: {cluster}\n"
                           f"Total: {total_prod:.0f}\nGrowth: {growth_rate:.2f}%")
        texts.append(ax.text(x, y, annotation_text, fontsize=9, ha='center',
                              bbox=dict(facecolor='white', edgecolor='darkgray', 
                                        boxstyle="round,pad=0.3", alpha=0.8)))

    # Adjust text positioning
    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))

    # Add centroid points
    ax.scatter(centroids.x, centroids.y, color='green', s=50, label='Centroid')

    # Add scale bar
    scalebar = ScaleBar(1, units="m", location='lower left', length_fraction=0.2)
    ax.add_artist(scalebar)

    # Set title and labels
    fig.suptitle('Production Clustering Map of Southeast Asia', fontsize=15, fontweight='bold')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, linestyle='--', alpha=1)

    return fig

def main():
    st.title('Southeast Asia Production Clustering Map')
    
    # Load data
    try:
        world, clustered_df = load_data()
        
        # Create map
        fig = create_sea_map(world, clustered_df)
        
        # Display map in Streamlit
        st.pyplot(fig)
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check the GitHub URLs and ensure files are accessible")

if __name__ == '__main__':
    main()
