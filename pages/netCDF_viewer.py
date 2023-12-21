import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import leafmap

import streamlit as st
from st_pages import add_page_title

add_page_title()


url = 'https://github.com/opengeos/leafmap/raw/master/examples/data/wind_global.nc'
filename = 'wind_global.nc'

leafmap.download_file(url, output=filename)

data = leafmap.read_netcdf(filename)





