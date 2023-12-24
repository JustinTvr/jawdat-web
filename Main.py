import streamlit as st
st.set_page_config(layout="wide")
import streamlit.components.v1 as components
from streamlit_extras.dataframe_explorer import dataframe_explorer 
from streamlit_extras.let_it_rain import rain 
from streamlit_extras.jupyterlite import jupyterlite 
from streamlit_extras.mandatory_date_range import date_range_picker 

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import utm
from pyproj import Proj
import seaborn as sns
import altair as alt
import geopandas as gpd
from shapely.geometry import Point
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import time

import io
import fiona
from fiona.io import ZipMemoryFile

from streamlit_folium import folium_static
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm

from st_pages import show_pages_from_config, add_page_title

show_pages_from_config("pages_sections.toml")
add_page_title()

st.text("Welcome to Jawdat-Web")

