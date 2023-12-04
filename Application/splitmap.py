import streamlit as st
import leafmap.foliumap as leafmap
import branca.colormap as cm
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Center-align the title
    st.markdown("<h1 style='text-align: center;'>Split-panel Map</h1>", unsafe_allow_html=True)

    # Sélecteur pour l'attribut (wider dropdown)
    attributs = ["vitesse", "temperature", "pression"]
    selected_attribut = st.selectbox("Sélectionner l'attribut", attributs, key='attribut_selector')

    # Create a row for the day selection buttons
    days_col1, days_col2 = st.columns(2)

    # Sélecteur pour le premier jour de la semaine
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    selected_jour1 = days_col1.selectbox("Sélectionner le premier jour de la semaine", jours, key='jour1_selector')

    # Sélecteur pour le deuxième jour de la semaine
    selected_jour2 = days_col2.selectbox("Sélectionner le deuxième jour de la semaine", jours, key='jour2_selector')

    # Construire les URLs en fonction des sélections de l'utilisateur
    left_image_url = f"https://kaoutar-elmouh.github.io/kaoutar-imane/nouveauxattributs/{selected_attribut}_{selected_jour1}.tif"
    right_image_url = f"https://kaoutar-elmouh.github.io/kaoutar-imane/nouveauxattributs/{selected_attribut}_{selected_jour2}.tif"

    # Create a leafmap Map
    m = leafmap.Map()

    # Définir les valeurs vmin et vmax en fonction de l'attribut sélectionné
    if selected_attribut == "vitesse":
        vmin, vmax = 0, 100
    elif selected_attribut == "temperature":
        vmin, vmax = 0, 20
    elif selected_attribut == "pression":
        vmin, vmax = 0, 50

    # Create a colormap with 6 equal intervals
    colormap = cm.LinearColormap(
        colors=[plt.cm.viridis(x) for x in np.linspace(0, 1, num=6)],
        index=np.linspace(vmin, vmax, num=6),
        vmin=vmin,
        vmax=vmax
    )
    m.add_child(colormap)

    m.split_map(left_image_url, right_image_url)

    # Render the map using st.pydeck_chart
    m.to_streamlit(height=700)

if __name__ == "__main__":
    main()