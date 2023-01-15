import streamlit as st
from  streamlit_folium import st_folium
import folium
from folium import plugins
from geopy.geocoders import Nominatim
import pandas as pd
import Flood_ml
import numpy as np


st.title(":blue[KUALA LUMPUR FLOOD PREDICTION]")
st.header("Prediction of flood occurances based on rainfall data")
st.write("---")
st.subheader(":blue[Method 1: Select Region of Interest By Adress]")
st.caption("Select the region of interest from drop down box")
# Create a text box for users to enter a street name
street_name = st.text_input("Enter street name or Region:")
geolocator = Nominatim(user_agent="wqd7003limee")
a=0
b=0
c=0


if street_name:
# Use the geocode() function to convert the street name into coordinates
    locations = geolocator.geocode(street_name, exactly_one=False)
    a=1
    # Create a dropdown menu with the suggested locations
    if locations is None:
        st.write(f":red[Location not found, Please Re-Enter]")
        locations = geolocator.geocode("Kuala Lumpur", exactly_one=False)
    
    
    location_list = [location.address for location in locations]
    location_selection = st.selectbox("Select a location:", location_list)

# Extract the latitude and longitude from the location object
    location = [location for location in locations if location.address == location_selection][0]
    latitude = location.latitude
    longitude = location.longitude

# Print the coordinates to the app
    st.write(f"Coordinates: {latitude}, {longitude}")
    loc=[latitude,longitude]
else:
    st.write(f"Type an adress")
    loc=[3.120125, 101.640258]


    

m=folium.Map(location=loc,zoom_start=16,width="%100",height="%80")
marker=folium.Marker(
    loc,
    popup="Selected Location for Prediction",
    tooltip="Selected Location",
    draggable=False
    
)
m.add_child(marker)


# Add custom base maps to folium
basemaps = {
    'Google Maps': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Maps',
        overlay = True,
        control = True
    ),
    'Google Satellite': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True
    ),
    'Google Terrain': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Terrain',
        overlay = True,
        control = True
    ),
    'Google Satellite Hybrid': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True
    ),
    'Esri Satellite': folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = True,
        control = True
    )
}

# Add custom basemaps
#basemaps['Google Satellite Hybrid'].add_to(m)

# Add a layer control panel to the map.
#m.add_child(folium.LayerControl())
current_loc=plugins.LocateControl(strings={"title": "Use Your Current Location", "popup": "Your Location"},)
m.add_child(current_loc)

#mouse position
fmtr = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
plugins.MousePosition(position='bottomleft', separator=' | ', prefix="loc:",lat_formatter=fmtr, lng_formatter=fmtr).add_to(m)

#call to render folium map in streamlit
st_data=st_folium(m,width=725)



#predict the flood occurance based on given rainfall data

#user key in rainfall data
st.subheader(":blue[Flood Prediction Based on the Address Selected]")
st.write("Selected Region:")

#a==1 means user keyed in valid location
if a==1:
    st.write(location)
    
#coordinate in loc [long,lat]
input_rainfall = st.text_input("Key in the expected rainfall in mm:")
st.markdown("<a href='https://publicinfobanjir.water.gov.my/hujan/data-hujan/?state=WLH&lang=en'>Refer to this link for rainfall data</a>", unsafe_allow_html=True)

if input_rainfall:
    try:
        result= float(input_rainfall)
        input_rainfall=float(input_rainfall)
    except TypeError:
        st.write(f":red[Please key in a valid number]")
        


#insert button to click and run prediction
if st.button(label="Predict!",key=1):
    stationID=Flood_ml.dist(loc)
    pred=Flood_ml.ml(stationID,input_rainfall)
    
    st.write("Nearest Rainfall Data Station Used for Prediction:")
    st.write(stationID)
    st.write("Prediction Result:")
      
    if pred==1:
        st.write(":red[FLOOD PREDICTED TO OCCUR, PLEASE BE CAUTIOUS]")
    else:
        st.write(":green[No Flood Predicted]")
        
   



    
#second section where csv is read and predicted        
st.write("---")
st.subheader(":blue[Method 2: Upload a CSV file with location and rainfall data for prediction]")
st.caption("The csv file should be formatted as shown below:")
st.image("csv_example.png")

file=st.file_uploader("Please upload the csv file")
if file:
    df_user=pd.read_csv(file)

if st.button(label="Predict!",key=2):
    #code for ML would go here
    csv_rainfall=df_user.iloc[:,1]
    df_user['Mapped Location'] = df_user.iloc[:,0].apply(lambda x: geolocator.geocode(x, exactly_one=True))
    lat=df_user['Mapped Location'].apply(lambda x:x.latitude)
    long=df_user['Mapped Location'].apply(lambda x:x.longitude)
    df_user['Mapped Coordinates']=list(zip(lat, long))
    
    #map to nearest station
    df_user['Nearest Rainfall Station ID']=df_user['Mapped Coordinates'].apply(lambda x:Flood_ml.dist(x))
    
    #prediction
    csv_station=df_user["Nearest Rainfall Station ID"]
    df_user["Prediction"]=Flood_ml.ml_df(csv_station,csv_rainfall)
    #convert to flood or no flood
    
    def dec(x):
        if x==1:
            a= "Flood"
        else:
            a= "No Flood"
        return a
    
    df_user['Prediction']=df_user['Prediction'].apply(lambda x:dec(x))
    
    st.write("Prediction Result:")
    st.table(df_user)
      


   