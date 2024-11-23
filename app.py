import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib_scalebar.scalebar import ScaleBar
from adjustText import adjust_text
from PIL import Image, ImageOps
import numpy as np
import tensorflow as tf
import folium
from branca.colormap import linear
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

# Fungsi untuk memproses gambar pada klasifikasi
def preprocess_image(image, target_size=(224, 224)):
    image = image.convert("RGB")
    image = ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
    image = np.asarray(image, dtype=np.float32)
    image = image / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# Fungsi Klasifikasi 1
def klasifikasi_1():
    st.title("🖼️ Klasifikasi 1: Spesies Ikan")
    st.markdown("""
    **Klasifikasi Gambar Spesies Ikan**
    - **Label 1:** Amphiprion clarkii
    - **Label 2:** Chaetodon lunulatus
    - **Label 3:** Chaetodon trifascialis
    """)
    uploaded_file = st.file_uploader("Upload gambar ikan (jpg, jpeg, png):", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar yang diunggah", use_column_width=True)
        st.warning("⏳ Memproses gambar...")
        processed_image = preprocess_image(image)
        prediction = model1.predict(processed_image)
        class_index = np.argmax(prediction)
        labels = ["Label 1 (Amphiprion clarkii)", "Label 2 (Chaetodon lunulatus)", "Label 3 (Chaetodon trifascialis)"]
        predicted_label = labels[class_index]
        probability = prediction[0][class_index] * 100
        st.success(f"🎉 **Prediksi:** {predicted_label}")
        st.info(f"**Probabilitas:** {probability:.2f}%")

# Fungsi Klasifikasi 2
def klasifikasi_2():
    st.title("🖼️ Klasifikasi 2: Spesies Ikan")
    st.markdown("""
    **Klasifikasi Gambar Spesies Ikan**
    - **Label 1:** Chromis Chrysura
    - **Label 2:** Dascyllus Reticulatus
    - **Label 3:** Plectroglyphidodon Dickii
    """)
    uploaded_file = st.file_uploader("Upload gambar ikan (jpg, jpeg, png):", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar yang diunggah", use_column_width=True)
        st.warning("⏳ Memproses gambar...")
        processed_image = preprocess_image(image)
        prediction = model2.predict(processed_image)
        class_index = np.argmax(prediction)
        labels = ["Label 1 (Chromis Chrysura)", "Label 2 (Dascyllus Reticulatus)", "Label 3 (Plectroglyphidodon Dickii)"]
        predicted_label = labels[class_index]
        probability = prediction[0][class_index] * 100
        st.success(f"🎉 **Prediksi:** {predicted_label}")
        st.info(f"**Probabilitas:** {probability:.2f}%")

# Fungsi untuk memuat data Clustering
def load_data():
    world_url = 'https://raw.githubusercontent.com/rifqi-qi/insight-clustering/refs/heads/main/world_map.geojson'
    clustered_data_url = 'https://raw.githubusercontent.com/rifqi-qi/insight-clustering/refs/heads/main/clustered_production_data.csv'
    world = gpd.read_file(world_url)
    clustered_df = pd.read_csv(clustered_data_url)
    return world, clustered_df

# Fungsi untuk membuat peta interaktif dengan Folium
def create_interactive_map(world, clustered_df):
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
    
    return m

# Fungsi untuk menampilkan peta interaktif
def interactive_map():
    st.title('Peta Interaktif Produksi Perikanan Asia Tenggara')
    try:
        world, clustered_df = load_data()
        m = create_interactive_map(world, clustered_df)
        st_folium(m, width=1500, height=800)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check the GitHub URLs and ensure files are accessible")

# Model untuk klasifikasi
model1 = tf.keras.models.load_model('akbar.h5')
model2 = tf.keras.models.load_model('dana.h5')

# Navigasi utama
def main():
    st.sidebar.title("Navigasi")
    option = st.sidebar.radio("Pilih Halaman:", ["Clustering", "Klasifikasi 1", "Klasifikasi 2", "Peta Interaktif"])
    if option == "Clustering":
        clustering()
    elif option == "Klasifikasi 1":
        klasifikasi_1()
    elif option == "Klasifikasi 2":
        klasifikasi_2()
    elif option == "Peta Interaktif":
        interactive_map()

if __name__ == "__main__":
    main()
