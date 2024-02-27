import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

elec_df_raw = load_data(path="./data/renewable_power_plants_CH.csv")
elec_df = deepcopy(elec_df_raw)

st.title("Electricity in Switzerland")
st.header("Here we will look into some interesting energy data!")

if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(data=elec_df)

########
    
left_column, middle_column, right_column = st.columns([3, 1, 1])

########


with open("./data/georef-switzerland-kanton.geojson", 'r') as response:
    electricity = json.load(response)

canton_names = {
'TG':'Thurgau', 
'GR':'Graubünden', 
'LU':'Luzern', 
'BE':'Bern', 
'VS':'Valais',                
'BL':'Basel-Landschaft', 
'SO':'Solothurn', 
'VD':'Vaud', 
'SH':'Schaffhausen', 
'ZH':'Zürich', 
'AG':'Aargau', 
'UR':'Uri', 
'NE':'Neuchâtel', 
'TI':'Ticino', 
'SG':'St. Gallen', 
'GE':'Genève',
'GL':'Glarus', 
'JU':'Jura', 
'ZG':'Zug', 
'OW':'Obwalden', 
'FR':'Fribourg', 
'SZ':'Schwyz', 
'AR':'Appenzell Ausserrhoden', 
'AI':'Appenzell Innerrhoden', 
'NW':'Nidwalden', 
'BS':'Basel-Stadt'}


elec_df['kan_name'] = elec_df['canton'].map(canton_names).astype(str)

########

plot_types = ["Matplotlib", "Plotly"]
plot_type = right_column.radio("Choose Plot Type", plot_types)


##########

#########

levels = ["All"]+sorted(pd.unique(elec_df['energy_source_level_2']))
level = left_column.selectbox("Choose your energy type", levels)


if level == "All":
    reduced_df = elec_df
else:
    reduced_df = elec_df[elec_df["energy_source_level_2"] == level]

#########

st.subheader("Electrical Capacity")

plotly_map = px.choropleth_mapbox(reduced_df, geojson=electricity, locations = 'kan_name', featureidkey= 'properties.kan_name' ,
                           color = 'electrical_capacity',
                           color_continuous_scale = 'earth',
                           range_color = [1,2],
                           title = 'Have you ever wondered which kanton has the highest electrical capacity? Of course you have, today you finally find out!',
                           zoom = 7, 
                           opacity = 0.2,
                           width = 1200,
                           height = 900,
                           labels = {'electrical_capacity':'Electrical Capacity', 'kan_name':'Name of Kanton'},
                           center = {"lat": 46.84, "lon": 8.34})

plotly_map.update_layout(mapbox_style="carto-positron")

st.plotly_chart(plotly_map)

#######################

st.subheader("Let's see how the prices change between the different energy types")

########## Mat

m_fig, ax = plt.subplots(figsize=(10, 8))
ax.bar(elec_df['energy_source_level_2'], elec_df['tariff'], alpha=0.7)

ax.set_title("Tariff for each energy type")
ax.set_xlabel('Energy type')
ax.set_ylabel('Tariff in CHF')

###################



############### Plotly

p_fig = px.bar(elec_df, x='energy_source_level_2', y='tariff', opacity=0.5,
                   width=750, height=600,
                   labels={"energy_source_level_2": "Energy type",
                           "tariff": "Tariff in CHF"},
                   title="Tariff for each energy type").update_traces(marker_line_width=0)
p_fig.update_layout(title_font_size=22)


################

if plot_type == "Matplotlib":
    st.pyplot(m_fig)
else:
    st.plotly_chart(p_fig)