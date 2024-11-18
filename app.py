import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib_scalebar.scalebar import ScaleBar
from io import BytesIO
import requests
import zipfile

# Fungsi utama untuk Streamlit
def main():
    st.title("Peta Hasil Clustering Produksi Ikan di Asia Tenggara")

    # URL file CSV dan Shapefile dari repository GitHub
    # Ganti URL di bawah ini dengan tautan ke file GitHub Anda
    csv_url = "https://raw.githubusercontent.com/rifqi-qi/insight-clustering/main/clustered_production_data.csv"
    shapefile_url = "https://github.com/rifqi-qi/insight-clustering/raw/main/ne_110m_admin_0_countries.zip"

    try:
        # Baca file CSV dari GitHub
        st.text("Memuat data clustering...")
        clustered_df = pd.read_csv(csv_url)
        st.success("File CSV berhasil dimuat dari GitHub!")

        # Unduh dan baca shapefile dari GitHub
        st.text("Memuat data peta...")
        response = requests.get(shapefile_url)
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall("shapefile")
        world = gpd.read_file("shapefile/ne_110m_admin_0_countries.shp")

        # Filter negara-negara Asia Tenggara
        sea_countries = ['Indonesia', 'Malaysia', 'Thailand', 'Vietnam', 'Philippines',
                         'Singapore', 'Brunei', 'Cambodia', 'Laos', 'Myanmar']
        sea_map = world[world['NAME'].isin(sea_countries)]

        # Gabungkan hasil clustering dengan data peta
        sea_map = sea_map.merge(clustered_df[['Entity', 'Cluster', 'total_production', 'growth_rate']],
                                left_on='NAME', right_on='Entity', how='left')

        # Reproyeksi GeoDataFrame ke proyeksi EPSG:3395 untuk akurasi centroid
        sea_map = sea_map.to_crs(epsg=3395)
        centroids = sea_map.geometry.centroid

        # Plot peta
        fig, ax = plt.subplots(1, 1, figsize=(14, 10), constrained_layout=True)

        # Tambahkan divider untuk legenda yang rapi
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)

        # Warna dan batas peta yang lebih soft
        sea_map.boundary.plot(ax=ax, linewidth=0, edgecolor="black")
        sea_map.plot(column='Cluster', ax=ax, legend=True, cmap='Spectral', edgecolor='darkgray',
                     legend_kwds={'shrink': 0.8}, cax=cax)

        # List untuk menyimpan objek teks anotasi
        texts = []

        # Anotasi centroid dengan style yang lebih informatif
        for centroid, label, total_prod, growth_rate, cluster in zip(centroids,
                                                                     sea_map['NAME'],
                                                                     sea_map['total_production'],
                                                                     sea_map['growth_rate'],
                                                                     sea_map['Cluster']):
            x, y = centroid.x, centroid.y
            annotation_text = (f"{label}\nCluster: {cluster}\nTotal: {total_prod:.0f}\nGrowth: {growth_rate:.2f}%")
            texts.append(ax.text(x, y, annotation_text, fontsize=9, ha='center',
                                 bbox=dict(facecolor='white', edgecolor='darkgray', boxstyle="round,pad=0.3", alpha=0.8)))

        # Gunakan adjust_text
        adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))

        # Tambahkan titik centroid untuk setiap negara
        ax.scatter(centroids.x, centroids.y, color='green', s=50, label='Centroid')

        # Tambahkan skala peta
        scalebar = ScaleBar(1, units="m", location='lower left', length_fraction=0.2)
        ax.add_artist(scalebar)

        # Set judul di level fig agar tetap di tengah
        fig.suptitle('Peta Hasil Clustering Produksi Ikan di Asia Tenggara', fontsize=15, fontweight='bold')

        # Set label sumbu dan grid
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.grid(True, linestyle='--', alpha=1)

        # Tampilkan peta di Streamlit
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

# Jalankan aplikasi
if __name__ == "__main__":
    main()
