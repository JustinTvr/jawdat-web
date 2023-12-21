
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

add_page_title()


nc_file = st.file_uploader('Select netCDF file', type=['nc'])

if nc_file is not None:
    dataset = xr.open_dataset(nc_file)
    st.code(dataset)


