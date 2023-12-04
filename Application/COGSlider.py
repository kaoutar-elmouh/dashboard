import rasterio
import streamlit as st
import folium
from folium import plugins
import matplotlib.pyplot as plt
from branca.colormap import LinearColormap
import numpy as np
import requests
from io import BytesIO

# Function to read the GeoTIFF file with rasterio
def read_geotiff(url):
    response = requests.get(url)
    dataset = rasterio.open(BytesIO(response.content))
    return dataset

# Fonction pour convertir l'image raster en une image compréhensible par Streamlit
def convert_to_streamlit_image(data):
    normalized_data = (data - data.min()) / (data.max() - data.min())
    return normalized_data

# Fonction pour récupérer les informations géospatiales
def get_geospatial_info(dataset):
    bounds = dataset.bounds
    transform = dataset.transform
    return {
        "Bounds": [bounds[0], bounds[1], bounds[2], bounds[3]],
        "CRS": str(dataset.crs),
        "Transform": [transform[0], transform[1], transform[2], transform[3], transform[4], transform[5]],
    }

def create_folium_map_with_mask_and_mouse_position(raster_layer, geospatial_info, attribute, day):
    # Zoom autour du point (33, -6) avec un niveau de zoom de 5
    m = folium.Map(location=[29, -9], zoom_start=5)

    # Ajouter la possibilité de dessiner sur la carte
    draw = plugins.Draw()
    draw.add_to(m)

    # Ajouter le mode plein écran
    plugins.Fullscreen().add_to(m)

    # Ajouter la fonctionnalité de position de la souris
    plugins.MousePosition().add_to(m)

    # Lire les données raster
    raster_data = raster_layer.read(1)

    # Créer un masque pour les valeurs égales à 0
    mask = raster_data != 0

    # Appliquer le masque à la donnée raster
    raster_data_masked = np.ma.masked_where(~mask, raster_data)

    # Définir la plage de couleurs en fonction de l'attribut
    if attribute == 'vitesse':
        # Plage spécifique pour l'attribut Vitesse
        vmin, vmax = 0, 100
    elif attribute == 'temperature':
        # Plage spécifique pour l'attribut Température
        vmin, vmax = 0, 20
    elif attribute == 'pression':
        # Plage spécifique pour l'attribut Pression
        vmin, vmax = 0, 50
    else:
        # Valeurs par défaut
        vmin, vmax = raster_data_masked.min(), raster_data_masked.max()

    # Définir la plage de couleurs avec 'viridis'
    cmap = plt.get_cmap('viridis')
    #  norm = plt.Normalize(vmin=vmin, vmax=vmax)
    norm = plt.Normalize(vmin=raster_data_masked.min(), vmax=raster_data_masked.max())

    # Modifier la ligne suivante pour ajuster les valeurs affichées sur la colormap
    num_classes = 5
    colormap = LinearColormap(
        colors=[cmap(norm(value)) for value in np.linspace(0, 255, num=num_classes)],
        vmin=vmin,
        vmax=vmax
    )

    # Créer une figure Matplotlib
    fig, ax = plt.subplots()
    img = ax.imshow(raster_data_masked, cmap=cmap, norm=norm)

    # Ajouter la couche raster à la basemap avec masque
    image_overlay = folium.raster_layers.ImageOverlay(
        image=img.to_rgba(raster_data_masked, bytes=True),
        bounds=[[geospatial_info["Bounds"][1], geospatial_info["Bounds"][0]],
                [geospatial_info["Bounds"][3], geospatial_info["Bounds"][2]]],
        colormap=lambda x: colormap(x),
    )
    image_overlay.add_to(m)

    # Ajouter la légende avec la barre de couleur
    colormap.add_to(m)


    return m

# Fonction principale Streamlit
def main():
    st.markdown("<h1 style='text-align: center;'>Naviguation entre les cartes format COG par SLIDER</h1>", unsafe_allow_html=True)

    # Sélection de l'attribut
    attributs = ['vitesse', 'temperature', 'pression']
    attribute = st.radio('Sélectionner un attribut :', attributs)

    # Liste des jours disponibles
    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    day = st.select_slider('Sélectionner un jour :', options=range(len(jours)), value=0, format_func=lambda i: jours[i])

    # Construction du chemin du fichier GeoTIFF
    file_url = f"https://kaoutar-elmouh.github.io/COGTIFF/COGTIFF/{attribute}_{jours[day]}.tif"

    # Vérifier si le fichier GeoTIFF existe
    try:
        dataset = read_geotiff(file_url)
    except rasterio.errors.RasterioIOError:
        st.error(f"Le fichier GeoTIFF {file_url} n'a pas pu être trouvé.")
        return

    # Récupération des informations géospatiales
    geospatial_info = get_geospatial_info(dataset)

    # Création de la basemap avec folium, ajout de la couche raster avec masque, et activation de l'affichage des valeurs
    folium_map = create_folium_map_with_mask_and_mouse_position(dataset, geospatial_info, attribute, jours[day])

    # Affichage de la basemap avec Streamlit
    st.write("Basemap avec la couche raster, masque, et affichage des valeurs :")
    st.components.v1.html(folium_map.get_root().render(), height=600)


if __name__ == "__main__":
    main()   

  


