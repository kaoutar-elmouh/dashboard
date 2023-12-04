import streamlit as st

def app():
    
    # Home page content
    
        st.title("Dashboard")

        # Larger image with a caption
        
        st.image("https://imane-byte.github.io/kkk/GIF/map3.gif", width=600, use_column_width=True)
            

        # Some text content
        st.write("""
            This is the home page of our awesome app. Here, you can find exciting content and explore various features.
            Feel free to navigate through different sections using the sidebar menu.
        """)

        # Styled button
        st.button("Click me!", key="home_button", help="This is a styled button")

        # Additional styled text
        st.markdown(
            """
            ### Additional Information
            
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed at augue ac velit efficitur varius in non urna.
            Duis vel arcu ac odio tristique dignissim. Integer ullamcorper ante in neque lacinia, ut scelerisque dui mollis.
            """
        )

    

        # Checkbox for additional options
        additional_options = st.checkbox("Enable additional options")

        if additional_options:
            # Interactive slider for customization
            customization_level = st.slider("Customization Level", min_value=1, max_value=10, value=5, step=1,
                                           help="Adjust the customization level")

            st.write(f"Selected Customization Level: {customization_level}")

            # Add more elements and options based on your needs

        st.info("Feel free to customize your settings!")

if __name__ == "__main__":
    app()
