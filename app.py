import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Judul aplikasi
st.title("Peta Clustering Produksi Ikan di Asia Tenggara")

# Upload file CSV
uploaded_file = st.file_uploader("Unggah file data clustering (CSV)", type="csv")
if uploaded_file is not None:
    # Membaca data dari file yang diunggah
    clustered_df = pd.read_csv(uploaded_file)

    # Data Koordinat Negara Asia Tenggara
    coordinates = {
        'Indonesia': [-0.7893, 113.9213],
        'Malaysia': [4.2105, 101.9758],
        'Thailand': [15.8700, 100.9925],
        'Philippines': [12.8797, 121.7740],
        'Vietnam': [14.0583, 108.2772],
        'Singapore': [1.3521, 103.8198],
        'Myanmar': [21.9162, 95.9560],
        'Cambodia': [12.5657, 104.9910],
        'Laos': [19.8563, 102.4955],
        'Brunei': [4.5353, 114.7277],
        'Timor-Leste': [-8.8742, 125.7275]
    }

    # Menambahkan koordinat ke DataFrame
    clustered_df['Latitude'] = clustered_df['Entity'].map(lambda x: coordinates[x][0] if x in coordinates else None)
    clustered_df['Longitude'] = clustered_df['Entity'].map(lambda x: coordinates[x][1] if x in coordinates else None)

    # Filter data dengan koordinat yang valid
    valid_data = clustered_df.dropna(subset=['Latitude', 'Longitude'])

    # Membuat peta
    seasia_map = folium.Map(location=[5.0, 110.0], zoom_start=5)

    # Menambahkan marker untuk setiap negara
    marker_cluster = MarkerCluster().add_to(seasia_map)
    for _, row in valid_data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"Negara: {row['Entity']}<br>Cluster: {row['Cluster']}",
            icon=folium.Icon(color='blue' if row['Cluster'] == 0 else 'red')
        ).add_to(marker_cluster)

    # Menampilkan peta di Streamlit
    st.subheader("Peta Clustering")
    folium_static(seasia_map)
else:
    st.warning("Unggah file CSV untuk menampilkan peta.")
