import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import linear
from folium.plugins import Fullscreen

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
        # Countries with cluster are colored, others are default map color (no fill)
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
    st.set_page_config(layout="wide")  # Set Streamlit layout to wide
    st.title('Southeast Asia Production Clustering Map')

    # Load data
    try:
        world, clustered_df = load_data()
        
        # Create map
        m = create_interactive_map(world, clustered_df)
        
        # Display map in Streamlit
        from streamlit_folium import st_folium
        st_folium(m, width=1500, height=800)  # Set large map size
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Please check the GitHub URLs and ensure files are accessible")

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

# Model untuk klasifikasi
model1 = tf.keras.models.load_model('akbar.h5')
model2 = tf.keras.models.load_model('dana.h5')

# Navigasi utama
def main():
    st.sidebar.title("Navigasi")
    option = st.sidebar.radio("Pilih Halaman:", ["Clustering", "Klasifikasi 1", "Klasifikasi 2"])
    if option == "Clustering":
        clustering()
    elif option == "Klasifikasi 1":
        klasifikasi_1()
    elif option == "Klasifikasi 2":
        klasifikasi_2()

if __name__ == '__main__':
    main()
