
import streamlit as st
import streamlit.components.v1 as components
from st_pages import add_page_title

import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import leafmap

import hvplot
import xarray as xr
import hvplot.pandas  # noqa
import hvplot.xarray  # noqa

import numpy as np
import pandas as pd
import geopandas as gpd
import holoviews as hv
from holoviews import opts
# hv.extension('bokeh')
from bokeh.models import HoverTool
from bokeh.plotting import figure, save
from bokeh.io import output_file

from io import StringIO
from io import BytesIO

import geoviews as gv
import cartopy.crs as ccrs

add_page_title()


nc_file = st.file_uploader('Select netCDF file', type=['nc'])

# @st.cache_resource(hash_funcs={xr.core.dataset.Dataset: id})
# def load_data(file):
#     file_content = file.read()
#     # Use content hash as the cache key
#     file_hash = hash(file_content)
#     # Use the hash as a key for caching
#     with BytesIO(file_content) as f:
#         data = xr.open_dataset(f)
#     return data

def use_file_for_hvplot(chart, chart_width=1000,chart_height=500):
    # Save the hvplot chart to an HTML file
    hvplot.save(chart,'temp.html')

    # Display the HTML in Streamlit
    with open("temp.html", 'r', encoding='utf-8') as f:
        html = f.read()
    components.html(html, width=chart_width,height=chart_height, scrolling=True)
st.bokeh_chart = use_file_for_hvplot

# @st.cache_data
def trouver_coords_lat_lon(_nc):

    lat_coord = None
    for coord_name in _nc.coords:
        if 'lat' in coord_name.lower():
            lat_coord = coord_name
            break
        elif 'y' == coord_name.lower():
            lat_coord = coord_name

    lon_coord = None
    for coord_name in _nc.coords:
        if 'lon' in coord_name.lower():
            lon_coord = coord_name
            break
        elif 'x' == coord_name.lower():
            lon_coord = coord_name

    return lat_coord, lon_coord

# @st.cache_data
def plot_quad(_dataset, _var, _latitude, _longitude, _tiles):
    data = _dataset[_var]

    dict_features = {'coastline': '110m'}

    quadmesh_plot = data.hvplot.quadmesh(
        x=_longitude, y=_latitude, z=_var,
        padding=0,
        global_extent=False,
        frame_height=400,
        frame_width=400,
        max_height = 400,
        max_width = 400,
        width=400,
        height = 400,
        features=dict_features,
        # widget_location='bottom',
        tiles=_tiles,
        alpha=0.5,
        project=True,
        geo=True,
        rasterize=True,
        dynamic=False,
    )

    st.bokeh_chart(quadmesh_plot)

if nc_file is not None:
    file_content = nc_file.read()

    # Use content hash as the cache key
    file_hash = hash(file_content)

    # Use the hash as a key for caching
    with xr.open_dataset(BytesIO(file_content)) as dataset:
        
        nc_coords = list(dataset.coords)
        nc_var = list(dataset.variables)
        nc_var = [x for x in nc_var if x not in nc_coords]

        with st.expander('Plot parameters'):
            sel_var = st.selectbox('Select the netCDF variables',nc_var)

            lat, lon = trouver_coords_lat_lon(dataset)
            st.text(f'{lat} and {lon} detected as spatial coordinates')

            list_tuiles = list(hv.element.tile_sources.keys())
            sel_tiles = st.selectbox('Select tiles', list_tuiles[::-1])    

        plot_quad(dataset, sel_var, lat, lon, sel_tiles)


    col1, col2 = st.columns(2)
    with col1:
        st.code(dataset)
    with col2:
        st.code(dataset.coords)
        st.code(dataset.variables)




