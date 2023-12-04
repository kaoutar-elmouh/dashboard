import streamlit as st
import geopandas as gpd
import folium
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
    st.markdown("<h1 style='text-align: center;'>REQUETE ATTRIBUTAIRE</h1>", unsafe_allow_html=True)

    # Ajouter une section pour le filtre (maintenant au-dessus de la carte)

    # Définir les opérateurs logiques disponibles
    operators = ['==', '!=', '>', '<', '>=', '<=']

    # Demander à l'utilisateur de spécifier les conditions pour chaque attribut
    num_conditions = st.number_input("Nombre de conditions", min_value=1, value=1)

    conditions = []
    for i in range(num_conditions):
        selected_column = st.selectbox(f"Sélectionner l'attribut {i + 1}", gdf.columns, key=f"select_{i}")
        operator = st.selectbox(f"Opérateur logique pour {selected_column}", operators, key=f"operator_{i}")
        condition_value = st.text_input(f"Condition pour {selected_column}", key=f"input_{i}")

        # Vérifier le type de données de la colonne et convertir la valeur de condition si nécessaire
        if gdf[selected_column].dtype == 'int64':
            condition_value = int(condition_value) if condition_value.isdigit() else condition_value

        conditions.append((selected_column, operator, condition_value))

    # Construire la requête de filtre en fonction des conditions saisies
    filter_query = " and ".join([f"{column} {operator} {value}" for column, operator, value in conditions if value and column in gdf.columns])

    # Appliquer le filtre
    if filter_query:
        filtered_gdf = gdf.query(filter_query)
        
        # Convertir la colonne de géométrie en chaîne de caractères
        filtered_gdf['geometry'] = filtered_gdf['geometry'].astype(str)
        
        # Utiliser Folium pour créer une carte
        m = folium.Map(location=[filtered_gdf['latitude'].mean(), filtered_gdf['longitude'].mean()], zoom_start=5)

        # Ajouter la possibilité de dessiner sur la carte
        draw = plugins.Draw()
        draw.add_to(m)

        # Ajouter le mode plein écran
        plugins.Fullscreen().add_to(m)

        # Ajouter la fonctionnalité de position de la souris
        plugins.MousePosition().add_to(m)

        for _, row in filtered_gdf.iterrows():
            folium.CircleMarker([row['latitude'], row['longitude']], radius=1, color='blue', fill=True, fill_color='purple').add_to(m)
        folium_static(m)

        # Afficher le tableau des données filtrées
        st.header("Données filtrées")
        st.dataframe(filtered_gdf)

    # Afficher la carte avec Streamlit en spécifiant les colonnes de latitude et de longitude
    else:
        # Convertir la colonne de géométrie en chaîne de caractères
        gdf['geometry'] = gdf['geometry'].astype(str)
        
        # Utiliser Folium pour créer une carte
        m = folium.Map(location=[gdf['latitude'].mean(), gdf['longitude'].mean()], zoom_start=5)

        # Ajouter la possibilité de dessiner sur la carte
        draw = plugins.Draw()
        draw.add_to(m)

        # Ajouter le mode plein écran
        plugins.Fullscreen().add_to(m)

        # Ajouter la fonctionnalité de position de la souris
        plugins.MousePosition().add_to(m)

        for _, row in gdf.iterrows():
            folium.CircleMarker([row['latitude'], row['longitude']], radius=1, color='blue', fill=True, fill_color='purple').add_to(m)
        folium_static(m)
