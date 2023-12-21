
import streamlit as st
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

from io import StringIO
from io import BytesIO

import geoviews as gv
import cartopy.crs as ccrs

add_page_title()


nc_file = st.file_uploader('Select netCDF file', type=['nc'])

@st.cache_resource(hash_funcs={xr.core.dataset.Dataset: id})
def load_data(file):
    file_content = file.read()
    # Use content hash as the cache key
    file_hash = hash(file_content)
    # Use the hash as a key for caching
    with BytesIO(file_content) as f:
        data = xr.open_dataset(f)
    return data

if nc_file is not None:
    dataset = load_data(nc_file)
    st.code(dataset)

    data = dataset['pr']

    dataset.close()

    dict_features = {'coastline':'110m',
              # 'lakes':'110m',
            #   'land':'110m',
            #   'ocean':'110m',
              # 'rivers':'50m',
            }

    quadmesh_plot = data.hvplot.quadmesh(
        'longitude', 'latitude', 'pr',
        # clim = (min_quad, max_quad),
        padding = 0,
        global_extent=False, 
        frame_height=540,
        # cmap='viridis',
        features=dict_features,
        widget_location='bottom',
        # widget_type='scrubber',
        # widgets={'time': pn.widgets.Select},
        alpha=0.5,
        # tiles='ESRI',
        project=True,
        geo=True,
        rasterize=True,
        dynamic=False,
        # projection=ccrs.Orthographic(center_lat, center_lon),
        # projection = ccrs.PlateCarree(),
    )


