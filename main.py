import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from backend import get_data, get_air_quality
import pandas as pd
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="Advanced Weather Forecast", layout="wide")

# Custom CSS to improve the app's appearance
# Hide Streamlit default menu and footer
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .reportview-container {
        background: linear-gradient(to right, #4880EC, #019CAD);
    }
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .medium-font {
        font-size:20px !important;
    }
    
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #2c3e50;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🌦️ Advanced Weather Forecast")
st.markdown("Get detailed weather information for any location worldwide!")

# Collapsible sidebar using st.expander
with st.expander("☰ Menu"):
    st.header("📍 Location Settings")
    place = st.text_input("Enter a city name:", "Osogbo", key="place_input")
    days = st.slider("Forecast Days", min_value=1, max_value=5, value=3, help="Select the number of forecasted days", key="days_slider")

    st.header("🔍 Data Options")
    temp_unit = st.radio("Temperature Unit:", ("Celsius", "Kelvin"), key="temp_unit_radio")

    show_hourly = st.checkbox("Show Hourly Forecast", value=False, key="show_hourly_checkbox")


# Function to convert temperature
def convert_temp(temp, to_unit):
    if to_unit == "Kelvin":
        return temp + 273.15
    return temp

# Main content
try:
    # Fetch data from backend
    data = get_data(place, days)

    # Display current weather
    st.header(f"Current Weather in {place}")
    col1, col2, col3 = st.columns(3)

    current_temp = convert_temp(data['current_weather']['temperature'], temp_unit)
    current_feels_like = convert_temp(data['current_weather']['feels_like'], temp_unit)

    with col1:
        st.metric("Temperature", f"{current_temp:.1f}°{'C' if temp_unit == 'Celsius' else 'K'}")
        st.metric("Humidity", f"{data['current_weather']['humidity']}%")

    with col2:
        st.metric("Feels Like", f"{current_feels_like:.1f}°{'C' if temp_unit == 'Celsius' else 'K'}")
        st.metric("Wind Speed", f"{data['current_weather']['wind_speed']} m/s")

    with col3:
        st.image(f"http://openweathermap.org/img/wn/{data['current_weather']['icon']}@2x.png", width=100)
        st.write(f"**{data['current_weather']['description'].capitalize()}**")

    # Air Quality Index
    try:
        aqi = get_air_quality(data['city_info']['coord']['lat'], data['city_info']['coord']['lon'])
        st.metric("Air Quality Index", aqi, help="1-2: Good, 3: Moderate, 4: Poor, 5: Very Poor")
    except Exception as e:
        st.warning("Unable to fetch air quality data.")

    # Daily forecast
    st.header("📅 Daily Forecast")
    daily_data = data['daily_forecast']
    df_daily = pd.DataFrame(daily_data).T
    df_daily.index = pd.to_datetime(df_daily.index)
    df_daily = df_daily.reset_index().rename(columns={'index': 'Date'})

    # Ensure dates are correct and in order
    today = datetime.now().date()
    df_daily['Date'] = [today + timedelta(days=i) for i in range(len(df_daily))]

    # Convert temperatures
    df_daily['temp_min'] = df_daily['temp_min'].apply(lambda x: convert_temp(x, temp_unit))
    df_daily['temp_max'] = df_daily['temp_max'].apply(lambda x: convert_temp(x, temp_unit))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_daily['Date'], y=df_daily['temp_max'], name='Max Temp', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df_daily['Date'], y=df_daily['temp_min'], name='Min Temp', line=dict(color='blue')))
    fig.update_layout(title='Temperature Forecast', xaxis_title='Date',
                      yaxis_title=f'Temperature (°{"C" if temp_unit == "Celsius" else "K"})')
    st.plotly_chart(fig)

    # Display daily data in columns
    cols = st.columns(len(df_daily))
    for idx, (_, row) in enumerate(df_daily.iterrows()):
        with cols[idx]:
            st.write(f"**{row['Date'].strftime('%b %d')}**")
            st.image(f"http://openweathermap.org/img/wn/{row['icon']}@2x.png", width=50)
            st.write(f"Max: {row['temp_max']:.1f}°{'C' if temp_unit == 'Celsius' else 'K'}")
            st.write(f"Min: {row['temp_min']:.1f}°{'C' if temp_unit == 'Celsius' else 'K'}")
            st.write(f"{row['description'].capitalize()}")

    # Precipitation Probability Bar Chart
    st.header("🌧️ Precipitation Probability")
    df_hourly = pd.DataFrame(data['forecast'])
    df_hourly['dt_txt'] = pd.to_datetime(df_hourly['dt_txt'])
    df_hourly['date'] = df_hourly['dt_txt'].dt.date
    daily_pop = df_hourly.groupby('date')['pop'].mean().reset_index()

    fig_pop = px.bar(daily_pop, x='date', y='pop',
                     labels={'pop': 'Probability of Precipitation', 'date': 'Date'},
                     title='Daily Precipitation Probability')
    fig_pop.update_traces(marker_color='skyblue')
    fig_pop.update_layout(yaxis_tickformat='.0%')
    st.plotly_chart(fig_pop)

    # Hourly forecast (if selected)
    if show_hourly:
        st.header("⏰ Hourly Forecast")
        df_hourly['temp'] = df_hourly['main'].apply(lambda x: convert_temp(x['temp'], temp_unit))

        fig = px.line(df_hourly, x='dt_txt', y='temp', title='Hourly Temperature Forecast')
        fig.update_layout(xaxis_title='Date and Time',
                          yaxis_title=f'Temperature (°{"C" if temp_unit == 'Celsius' else 'K'})')
        st.plotly_chart(fig)

    # Additional city information
    st.header("🏙️ City Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Country:** {data['city_info']['country']}")
        st.write(f"**Timezone:** UTC{data['city_info']['timezone'] // 3600:+d}")
    with col2:
        st.write(f"**Sunrise:** {pd.to_datetime(data['city_info']['sunrise'], unit='s').strftime('%H:%M:%S')}")
        st.write(f"**Sunset:** {pd.to_datetime(data['city_info']['sunset'], unit='s').strftime('%H:%M:%S')}")

    # Disclaimer
    st.info("Note: Forecast data is based on a free API subscription and may change when the subscription expires.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please make sure you've entered a valid city name and try again.")

# Footer
st.markdown(
        """
        <div class="footer">
        © 2024 All Rights Reserved | Dr. Ridwan Oladipo
        </div>
        """,
        unsafe_allow_html=True
    )
