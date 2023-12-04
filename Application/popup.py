import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import altair as alt
from decimal import Decimal
from streamlit_folium import folium_static
from folium import plugins
import requests
from io import BytesIO

def app():
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
    st.markdown("<div style='text-align: center;'><h1>Visualisation des graphiques des attributs des points</h1></div>", unsafe_allow_html=True)

    # Liste des jours
    Jour = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

    # Créer une carte Folium
    m = folium.Map(location=[gdf['latitude'].mean(), gdf['longitude'].mean()], zoom_start=5)

    # Ajouter la possibilité de dessiner sur la carte
    draw = plugins.Draw()
    draw.add_to(m)

    # Ajouter le mode plein écran
    plugins.Fullscreen().add_to(m)

    # Ajouter la fonctionnalité de position de la souris
    plugins.MousePosition().add_to(m)

    for index, row in gdf.iterrows():
        marker = folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=1, color='red', fill=True, fill_color='red')

        data = {
            'Jour': list(range(1, 8)),
            'Vitesse_vent': [float(row[f'Vitesse_vent_{jour}']) for jour in Jour],
            'Temperature': [float(row[f'Temperature_{jour}']) for jour in Jour],
            'Pression': [float(row[f'Pression_{jour}']) for jour in Jour]
        }

        df_chart = pd.DataFrame(data).melt('Jour')

        chart = alt.Chart(df_chart).mark_line().encode(
            x='Jour:O',
            y='value:Q',
            color='variable:N',
            tooltip=['variable:N', 'value:Q']
        ).properties(width=300, height=150)

        popup = folium.Popup(max_width=350).add_child(folium.VegaLite(chart, width=350, height=150))
        marker.add_child(popup)
        marker.add_to(m)

    # Afficher la carte Folium dans Streamlit
    folium_static(m)
