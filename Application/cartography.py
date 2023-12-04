
import streamlit as st
import geopandas as gpd
import folium
from folium import plugins
from streamlit_folium import folium_static
from shapely.geometry import mapping
import matplotlib.pyplot as plt
import requests
from io import BytesIO

def app() :
    
    def download_file(url):
        response = requests.get(url)
        return BytesIO(response.content)


    # Charger les données à partir de l'URL
    file_url = "https://kaoutar-elmouh.github.io/DATA/DATA/DATANEW.geoparquet"
    file_path = download_file(file_url)
    gdf = gpd.read_parquet(file_path)

    # Liste des attributs et jours disponibles
    attributs = [att for att in gdf.columns[1:-1] if att != 'Date']  # Exclure l'attribut 'Date'
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

    # Placeholder for the title
    title_placeholder = st.empty()

    # Bold title in the middle at the top of the page
    title_placeholder.markdown("<h1 style='text-align: center; font-weight: bold;'>LA CARTOGRAPHIE THEMATIQUE</h1>", unsafe_allow_html=True)

    # Sélection de l'attribut
    attribut = st.selectbox('Sélectionner un attribut a cartographier :', attributs)

    # Construire le nom de la colonne en fonction de la sélection
    colonne_selectionnee = f"{attribut}"  # Convertir le jour en majuscules pour correspondre aux données

    # Créer la carte avec Folium
    m = folium.Map(location=[29.19, -9], zoom_start=5)

    # Ajouter la fonctionnalité de position de la souris
    plugins.MousePosition().add_to(m)

    # Vérifier si la colonne sélectionnée existe dans le GeoDataFrame
    if colonne_selectionnee not in gdf.columns:
        st.error(f"La colonne {colonne_selectionnee} n'existe pas dans le GeoDataFrame.")
    else:
        # Convertir les valeurs de la colonne en nombres flottants
        gdf[colonne_selectionnee] = gdf[colonne_selectionnee].astype(float)

        # Diviser les données en 5 classes
        nb_classes = 5
        class_bins = [gdf[colonne_selectionnee].quantile(i / nb_classes) for i in range(nb_classes + 1)]
        colors = ['#440154', '#39568C', '#1F968B', '#73D055', '#FDE725']

        # Définir la colormap
        colormap = folium.LinearColormap(colors=colors, vmin=gdf[colonne_selectionnee].min(), vmax=gdf[colonne_selectionnee].max())

        # Ajouter manuellement les classes à la carte Folium
        colormap.add_to(m)

        # Ajouter la classification de couleur à la carte Folium
        for index, row in gdf.iterrows():
            value = row[colonne_selectionnee]
            color = colormap(value)

            # Utiliser folium.Polygon pour simuler un rectangle
            rectangle = folium.Polygon(
                locations=[(row.geometry.y - 0.03, row.geometry.x - 0.03),
                        (row.geometry.y - 0.03, row.geometry.x + 0.03),
                        (row.geometry.y + 0.03, row.geometry.x + 0.03),
                        (row.geometry.y + 0.03, row.geometry.x - 0.03)],
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                tooltip=f"Value: {value}"
            )
            rectangle.add_to(m)

        # Ajouter la possibilité de dessiner sur la carte
        draw = plugins.Draw()
        draw.add_to(m)

        # Ajouter le mode plein écran
        plugins.Fullscreen().add_to(m)

        # Afficher la carte Folium dans Streamlit
        folium_static(m)



