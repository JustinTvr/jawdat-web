
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

if nc_file is not None:
    file_content = nc_file.read()

    # Use content hash as the cache key
    file_hash = hash(file_content)

    # Use the hash as a key for caching
    with xr.open_dataset(BytesIO(file_content)) as dataset:
        st.code(dataset)

        data = dataset['t2m']

        dict_features = {'coastline': '110m'}

        quadmesh_plot = data.hvplot.quadmesh(
            'longitude', 'latitude', 't2m',
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
            alpha=0.5,
            project=True,
            geo=True,
            rasterize=True,
            dynamic=False,
        )

        st.bokeh_chart(quadmesh_plot)


