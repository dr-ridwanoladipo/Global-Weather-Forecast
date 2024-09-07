import streamlit as st
import plotly.express as px
from backend import get_data

# Add title and user inputs
st.title("Weather Forecast for the Next Days")

# Text input for place
place = st.text_input("Place: ")

# Slider for number of forecast days
days = st.slider("Forecast Days", min_value=1, max_value=5, help="Select the number of forecasted days")

# Selectbox for data type
option = st.selectbox("Select data to view", ("Temperature", "Sky"))

st.subheader(f"{option} for the next {days} days in {place}")

if place:
    try:
        # Fetch data from backend
        filtered_data = get_data(place, days)

        # Display temperature data
        if option == "Temperature":
            temperatures = [data["main"]["temp"] / 10 for data in filtered_data]
            dates = [data["dt_txt"] for data in filtered_data]

            # Create and display a temperature plot
            figure = px.line(x=dates, y=temperatures, labels={"x": "Date", "y": "Temperature (°C)"})
            st.plotly_chart(figure)

        # Display sky conditions
        if option == "Sky":
            images = {
                "Clear": "images/clear.png",
                "Clouds": "images/cloud.png",
                "Rain": "images/rain.png",
                "Snow": "images/snow.png"
            }
            sky_conditions = [data["weather"][0]["main"] for data in filtered_data]
            image_paths = [images[condition] for condition in sky_conditions]
            st.image(image_paths, width=115)

    except KeyError:
        st.write("That place does not exist.")
