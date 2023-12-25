
import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.stateful_button import button
from streamlit_extras.stoggle import stoggle
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

import os

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

# @st.cache_resource
def use_file_for_hvplot(_chart, temp_name,chart_width=1000,chart_height=500):
    if os.path.exists(temp_name):
        os.remove(temp_name)
    
    # Save the hvplot chart to an HTML file
    hvplot.save(_chart,temp_name)

    # Display the HTML in Streamlit
    # with open("temp.html", 'r', encoding='utf-8') as f:
    #     html = f.read()
    # components.html(html, width=chart_width,height=chart_height, scrolling=True)
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
def plot_nc(_dataset, _var, _latitude, _longitude, _tiles,_color):
    # st.cache_resource.clear()
    
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
        cmap=_color,
        alpha=0.5,
        project=True,
        geo=True,
        rasterize=True,
        dynamic=False,
    )

    st.bokeh_chart(quadmesh_plot, 'quadmesh.html')

def make_toggle_false():
    if btn_apply:
        st.session_state.toggle_nc = False



if nc_file is not None:
    plot_created = False

    @st.cache_data
    def read_nc(file):
        file_content = file.read()

        # Use content hash as the cache key
        file_hash = hash(file_content)

        # Use the hash as a key for caching
        with xr.open_dataset(BytesIO(file_content)) as open_dataset:
            return open_dataset

    dataset = read_nc(nc_file)

    nc_coords = list(dataset.coords)
    nc_var = list(dataset.variables)

    nc_var = [x for x in nc_var if x not in nc_coords]
    nc_var = [x for x in nc_var if 'time' not in x]

    show_metadata = st.checkbox('Show metadata')
    maintab_nc, coord_nc, history_nc = st.tabs(['Dataset', 'Coordinates', 'History'])
    if show_metadata:
        with maintab_nc :
            st.code(dataset)
        with coord_nc:
            st.code(dataset.coords)
        with history_nc:
            st.code(dataset.history)


    with st.expander('Plot parameters'):
        st.write('Select your parameter and click on apply button')

        sel_var = st.selectbox('Select the netCDF variables',nc_var)

        lat, lon = trouver_coords_lat_lon(dataset)
        st.text(f'{lat} and {lon} detected as spatial coordinates')

        list_tuiles = list(hv.element.tile_sources.keys())
        sel_tiles = st.selectbox('Select tiles', list_tuiles, index=list_tuiles.index('OpenTopoMap'))    

        list_colors = list(hv.plotting.list_cmaps())
        id_pr_color = list_colors.index('YlGnBu')
        id_tas_color = list_colors.index('hot_r')
        list_potential_temp = ['t2m','tas']
        if ('pr' in sel_var) :
            sel_index = id_pr_color
        elif id_tas_color in list_potential_temp:
            sel_index = id_tas_color
        else :
            sel_index = list_colors.index('blues')

        sel_color = st.selectbox('Select colors',list_colors, index = sel_index) 
        stoggle(
        "Which palette to choose ?",
        "'YlGnBu' for precipitation data, 'hot_r' for temperature, 'coolwarm' for comparison/bias data\n\
Add _r to all palette to reverse it")

        btn_apply = st.toggle('Apply', key='toggle_nc')
        

    if btn_apply:
        # make_toggle_false()
        with st.spinner('Creating plot...'):
            plot_nc(dataset, sel_var, lat, lon, sel_tiles, sel_color)

        with open("quadmesh.html", 'r', encoding='utf-8') as f:
            html = f.read()
        components.html(html, width=1000,height=500, scrolling=True)

        
###############################################
with st.expander('How to reproduce this plot'):
    code = '''
    import xarray as xr

    dataset = xr.open_dataset('path_to_nc')

    data = dataset[var]

    dict_features = {'coastline': '110m'}

    quadmesh_plot = data.hvplot.quadmesh(
        x=longitude, y=latitude, z=var,
        padding=0,
        global_extent=False,
        frame_height=400,
        frame_width=400,
        max_height = 400,
        max_width = 400,
        width=400,
        height = 400,
        features=dict_features,
        # widget_location='bottom', # choose widget location, to save the plot you need to comment it
        tiles=tiles,
        cmap=color,
        alpha=0.5,
        project=True,
        geo=True,
        rasterize=True,
        dynamic=False,
    )'''
    st.code(code, language='python')



