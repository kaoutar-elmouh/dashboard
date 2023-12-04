import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
from math import radians, sin, cos, sqrt, atan2
import folium
from streamlit_folium import folium_static
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

    # Titre de l'application Streamlit
    st.markdown("<h1 style='text-align: center;'>REQUETE SPATIALE</h1>", unsafe_allow_html=True)

    # Entrée utilisateur pour les coordonnées et le rayon
    latitude = st.number_input("Latitude:")
    longitude = st.number_input("Longitude:")
    rayon = st.number_input("Rayon:")

    # Créer le point à partir des coordonnées entrées par l'utilisateur
    user_point = Point(longitude, latitude)

    def haversine(lat1, lon1, lat2, lon2):
        # Vérifier si les coordonnées sont les mêmes
        if lat1 == lat2 and lon1 == lon2:
            return 0
        
        R = 6371  # Rayon de la Terre en kilomètres

        # Conversion des coordonnées de degrés à radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Calcul des écarts angulaires
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Formule de la haversine
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Distance en kilomètres
        distance = R * c

        return distance

    # Extraire les coordonnées de la colonne "geometry"
    gdf['longitude'] = gdf['geometry'].x
    gdf['latitude'] = gdf['geometry'].y

    # Filtrer les points à l'intérieur du cercle défini par l'utilisateur
    gdf["distance_to_user"] = gdf.apply(lambda row: haversine(latitude, longitude, row['latitude'], row['longitude']), axis=1)
    filtered_gdf = gdf[gdf["distance_to_user"] <= rayon]

    # Créer une carte avec folium
    m = folium.Map(location=[latitude, longitude], zoom_start=5, control_scale=True)

    # Ajouter un marqueur pour le point utilisateur
    folium.Marker([latitude, longitude], popup="Point utilisateur", icon=folium.Icon(color="red")).add_to(m)

    # Ajouter des marqueurs pour les points à l'intérieur du cercle
    for index, row in filtered_gdf.iterrows():
        folium.Marker([row['latitude'], row['longitude']], popup=f"Point {index}", icon=folium.Icon(color="blue")).add_to(m)

    # Ajouter la possibilité de dessiner sur la carte
    draw = plugins.Draw()
    draw.add_to(m)

    # Ajouter le mode plein écran
    plugins.Fullscreen().add_to(m)

    # Ajouter la fonctionnalité de position de la souris
    plugins.MousePosition().add_to(m)

    # Afficher la carte avec les marqueurs
    folium_static(m)

    # Afficher la table des points à l'intérieur du cercle
    st.write("Points à l'intérieur du cercle:")
    st.write(filtered_gdf)

    # Ajouter un bouton de téléchargement pour le tableau filtré
    if not filtered_gdf.empty:
        csv_data = filtered_gdf.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="Télécharger le tableau filtré en CSV",
            data=csv_data,
            file_name="tableau_filtre.csv",
            key="download_button"
        )
