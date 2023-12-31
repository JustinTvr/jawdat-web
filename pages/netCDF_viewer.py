
import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.stateful_button import button
from streamlit_extras.stoggle import stoggle
from streamlit_extras.add_vertical_space import add_vertical_space
from annotated_text import annotated_text
from st_pages import add_page_title

import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import leafmap

import hvplot
import xarray as xr
import hvplot.pandas  # noqa
import hvplot.xarray  # noqa

import packages.df_function as dff
import packages.st_dict_input as stdict

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

# @st.cache_data
def use_file_for_hvplot(_chart, temp_name,chart_width=1000,chart_height=600):
    if os.path.exists(temp_name):
        os.remove(temp_name)
    
    # Save the hvplot chart to an HTML file
    hvplot.save(_chart,temp_name)
    # Display the HTML in Streamlit
    with open(temp_name, 'r', encoding='utf-8') as f:
        html = f.read()
        # return html
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
def plot_nc(_dataset, _var, _latitude, _longitude, _tiles,_color, alpha):
    # st.cache_resource.clear()
    if alpha == 1.0:
        rasterize = True
    else :
        rasterize = False
    
    data = _dataset[_var]

    if type(_tiles) == dict :
        dict_features = _tiles  
        param_tiles = None
    else :
        dict_features = None
        param_tiles = _tiles

    ### For now not working due to hvplot save, same error if 
    params = {
        # 'clim': (min_quad, max_quad),
        'padding': 0,
        'global_extent': False,
        'frame_height':400,
        'frame_width':400,
        'max_height': 400,
        'max_width' : 400,
        'width':400,
        'height' : 400,
        # 'cmap': 'viridis',
        'features': dict_features,
        # 'widget_location': 'bottom',
        # 'widget_type': 'scrubber',
        # 'widgets': {'time': pn.widgets.Select},
        'alpha': alpha,
        'cmap': _color,
        'tiles': param_tiles,
        'project': True,
        'geo': True,
        'rasterize': rasterize,
        'dynamic': False,
        # 'projection': ccrs.Orthographic(center_lat, center_lon),
        # 'projection': ccrs.PlateCarree(),
    }

    quadmesh_plot = data.hvplot.quadmesh(x=_longitude, y=_latitude, z=_var,**params)

    return quadmesh_plot
    # st.bokeh_chart(quadmesh_plot, 'quadmesh.html')


if nc_file is not None:
    plot_created = False

    @st.cache_data
    def read_nc(file):
        st.cache_resource.clear()

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
        def disable_apply():
            st.session_state.button_nc = False
    
        st.write('Select your parameter and click on apply button')
        st.divider()

        ########################
        var_col, col_col, tiles_col = st.columns(3)
        with var_col:
            sel_var = st.selectbox('Select the netCDF variables',nc_var, on_change=disable_apply)

            lat, lon = trouver_coords_lat_lon(dataset)
            st.text(f'{lat} and {lon} detected as spatial coordinates')

        with col_col:
            st.link_button('Holoview color','https://holoviews.org/user_guide/Colormaps.html')
            list_colors = list(hv.plotting.list_cmaps())
            id_pr_color = list_colors.index('YlGnBu')
            id_tas_color = list_colors.index('hot_r')
            list_potential_temp = ['t2m','tas']
            if ('pr' in sel_var) :
                sel_index = id_pr_color
            elif sel_var in list_potential_temp:
                sel_index = id_tas_color
            else :
                sel_index = list_colors.index('blues')

            sel_color = st.selectbox('Select colors',list_colors, index = sel_index, on_change=disable_apply) 
            annotated_text(('YlGnBu','Precipitation',"#8ef"),' | ',
                        ('hot_r','Temperature',"#faa"),' | ',
                        ('coolwarm','Bias',"#fea"),' | ',
                        ('_r','To reverse palette',"#afa"),
                        )

        with tiles_col:
            toggle_tiles = st.toggle('Add background tiles', value=True, on_change=disable_apply)
            if toggle_tiles:
                list_tuiles = list(hv.element.tile_sources.keys())
                list_tuiles = ['CartoDark', 'CartoEco', 'CartoLight', 'CartoMidnight', 'EsriAntarcticImagery', 'EsriArcticImagery', 'EsriArcticOceanBase', 'EsriArcticOceanReference', 'EsriDelormeWorldBaseMap', 'EsriImagery', 'EsriNatGeo', 'EsriOceanBase', 'EsriOceanReference', 'EsriReference', 'EsriTerrain', 'EsriUSATopo', 'EsriWorldBoundariesAndPlaces', 'EsriWorldBoundariesAndPlacesAlternate', 'EsriWorldDarkGrayBase', 'EsriWorldDarkGrayReference', 'EsriWorldHillshade', 'EsriWorldHillshadeDark', 'EsriWorldLightGrayBase', 'EsriWorldLightGrayReference', 'EsriWorldNavigationCharts', 'EsriWorldPhysical', 'EsriWorldShadedRelief', 'EsriWorldStreetMap', 'EsriWorldTopo', 'EsriWorldTransportation', 'OSM', 'OpenTopoMap']
                sel_tiles = st.selectbox('Select tiles', list_tuiles, index=list_tuiles.index('OpenTopoMap'), on_change=disable_apply)   
            else :
                sel_tiles = st.multiselect('Select map features',['land','coastline','ocean','rivers','lakes'], on_change=disable_apply)
                
                df_features = pd.DataFrame(sel_tiles, columns=['Features'])
                df_features['Precisions [m] - 10/50/110'] = 110
                df_features.set_index('Features', inplace=True)
                df_feature_user = st.data_editor(df_features,hide_index=False, disabled=['Features'],use_container_width=True, on_change=disable_apply)

                dict_good = True
                for index, value in enumerate(df_feature_user['Precisions [m] - 10/50/110']):
                    if value not in {10, 50, 110}:
                        st.warning(f'Warning: Value {value} not in 10,50,110, please change the value for {df_feature_user.index[index]}')
                        dict_good = False
                if dict_good :
                    df_feature_user['Precisions [m] - 10/50/110'] = df_feature_user['Precisions [m] - 10/50/110'].astype(str) + 'm'
                    sel_tiles = df_feature_user.to_dict().popitem()[1]


        ########################
    
        st.divider() 


        ########################
        alpha_col1, alpha_col2 =st.columns(2)
        with alpha_col1:
            choice_alpha = st.toggle('Change transparency ? (plot will not be rasterized anymore)', on_change=disable_apply)
        if choice_alpha:
            with alpha_col2:
                sel_alpha = st.slider('Select transparency',min_value=0.0,max_value=1.0,value=0.7, step=0.1, on_change=disable_apply)
        else :
            sel_alpha = 1.0
        ###########
        st.divider()
        btn_apply = st.toggle('Apply', key='button_nc')

    if btn_apply:
        with st.spinner('Creating plot...'):
            output_quad = plot_nc(dataset, sel_var, lat, lon, sel_tiles, sel_color, sel_alpha)
        with st.spinner('Creating html to display...'):
            st.bokeh_chart(output_quad, 'quadmesh.html')
    

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

# test = {'coastline':110,
#         'rivers':110,
#         }

# test = pd.DataFrame(
#     [
#         {"command": "coastline", "rating": 4},
#         {"command": "rivers", "rating": 5},
#     ]
# )

# test_output = st.data_editor(test,num_rows='dynamic', disabled=["command"])

# st.write(dict(test_output))