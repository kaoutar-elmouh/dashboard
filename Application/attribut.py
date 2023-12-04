import streamlit as st
import geopandas as gpd
import folium
from folium import plugins
import requests
from io import BytesIO

def app() :
    def download_file(url):
        response = requests.get(url)
        return BytesIO(response.content)

    # Charger le fichier Parquet avec geopandas
    file_url = "https://kaoutar-elmouh.github.io/DATA/DATA/DATANEW.geoparquet"
    file_path = download_file(file_url)
    gdf = gpd.read_parquet(file_path)

    # Extraire les coordonnées de latitude et de longitude à partir de la colonne de géométrie
    gdf['latitude'] = gdf['geometry'].y
    gdf['longitude'] = gdf['geometry'].x

    # Créer une application Streamlit
    st.markdown("<h1 style='text-align: center;'>Recherche de point avec ses coordonnées</h1>", unsafe_allow_html=True)

    # Ajouter une textbox pour saisir les coordonnées
    coordinates = st.text_input("Entrez les coordonnées (format : latitude, longitude)", "")

    # Créer une carte Folium
    m = folium.Map(location=[gdf['latitude'].mean(), gdf['longitude'].mean()], zoom_start=5)

    # Ajouter les cercles pour les autres points
    for index, row in gdf.iterrows():
        folium.CircleMarker([row['latitude'], row['longitude']], radius=1, color='blue', fill=True, fill_color='purple').add_to(m)

    # Ajouter la possibilité de dessiner sur la carte
    draw = plugins.Draw()
    draw.add_to(m)

    # Ajouter le mode plein écran
    plugins.Fullscreen().add_to(m)

    # Ajouter la fonctionnalité de position de la souris
    plugins.MousePosition().add_to(m)

    # Vérifier si des coordonnées ont été saisies
    if coordinates:
        # Diviser les coordonnées saisies en latitude et longitude
        try:
            lat, lon = map(float, coordinates.split(','))

            # Ajouter le marqueur pour le point recherché
            folium.Marker([lat, lon], popup='Point Recherché', icon=folium.Icon(color='red')).add_to(m)

        except ValueError:
            st.error("Format incorrect. Assurez-vous d'utiliser le format correct : latitude, longitude")

    # Générer le code HTML de la carte Folium
    map_html = m.get_root().render()

    # Afficher la carte avec Streamlit
    st.components.v1.html(map_html, height=600)

if __name__ == "__main__":
    app()
