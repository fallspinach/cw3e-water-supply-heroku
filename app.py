import os

import dash
from dash import dcc
from dash import html
from dash.dependencies import ClientsideFunction, Input, Output
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import Namespace, arrow_function, assign

from datetime import date, datetime, timedelta

# temporary set up
curr_day   = datetime(2022, 1, 6)
data_start = datetime(2021, 6, 1)
data_end   = datetime(2022, 1, 6)


## data variable selection dropdown
var_longnames = ['2-m SM Percentile', 'SWE Percentile']
var_names = ['smtot_r', 'swe_r']

options_data = [dict(label=var_longnames[i], value=i) for i in range(len(var_longnames))]
dropdown_data = dcc.Dropdown(options=options_data, value=0, id='dropdown-data', clearable=False)

layer_var_select = html.Div([dropdown_data], id='layer-var-select-container')


## CW3E logo
logo_cw3e = html.A(html.Img(src='assets/cw3e_logo_80.png', title='CW3E Home', sizes='64px, 80px'), href='https://cw3e.ucsd.edu/', id='logo-cw3e')

## B-120 forecast points

point_to_layer = assign('''function(feature, latlng, context){
    const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
    circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop.
    return L.circleMarker(latlng, circleOptions);  // sender a simple circle marker.
}''')

fcst_points = dl.GeoJSON(url='assets/fnf_points_proj_tooltip.pbf', format='geobuf', id='points',
                         options=dict(pointToLayer=point_to_layer), cluster=True, superClusterOptions=dict(radius=5),
                         hoverStyle=arrow_function(dict(weight=5, color='red', fillColor='red', dashArray='')),
                         hideout=dict(circleOptions=dict(fillOpacity=1, color='red', weight=2, radius=5), colorscale=['cyan'], colorProp='POINT_Y', min=0, max=100))


## B-120 watersheds

watershed_style = dict(weight=2, opacity=1, color='darkblue', fillOpacity=0)
style_handle = assign('''function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}''')

fcst_watersheds = dl.GeoJSON(url='assets/fnf_watershed_proj_tooltip.pbf', format='geobuf', id='watershed',
                             options=dict(style=style_handle),
                             hoverStyle=arrow_function(dict(weight=4, color='brown', dashArray='', fillOpacity=0)),
                             hideout=dict(colorscale=['darkblue'], classes=[0], style=watershed_style, colorProp='Area_SqMi'))

## CNRFC boundary

cnrfc_style = dict(weight=4, opacity=1, color='gray', fillOpacity=0)
cnrfc_boundary = dl.GeoJSON(url='assets/cnrfc_bd_degree_wgs84.pbf', format='geobuf', id='cnrfcbd',
                             options=dict(style=style_handle),
                             hideout=dict(colorscale=['black'], classes=[0], style=cnrfc_style, colorProp='Area_SqMi'))

## image data layer

cnrfc_domain = [[32, -125], [44, -113]]
base_url = 'https://cw3e.ucsd.edu/wrf_hydro/cnrfc/imgs/'
#img_url = base_url + curr_day.strftime('monitor/output/%Y/smtot_r_%Y%m%d%') + var_names[dropdown_forcing.value] + '.png'
img_url = base_url + curr_day.strftime('monitor/output/%Y/smtot_r_%Y%m%d.png')
data_map = dl.ImageOverlay(id='data-img', url=img_url, bounds=cnrfc_domain, opacity=0.6)

# color bar
data_cbar = html.A(html.Img(src='https://cw3e.ucsd.edu/wrf_hydro/cnrfc/imgs/monitor/output/smtot_r_cbar.png', title='Color Bar', id='data-cbar-img'), id='data-cbar')


## all layers
locator = dl.LocateControl(options={'locateOptions': {'enableHighAccuracy': True}})
map_cnrfc = dl.Map([dl.TileLayer(), locator,
                    dl.LayersControl([dl.Overlay([data_map, data_cbar], id='data-map',        name='Data',        checked=True),
                                      dl.Overlay(cnrfc_boundary,        id='cnrfc-boundary',  name='CNRFC',       checked=True),
                                      dl.Overlay(fcst_watersheds,       id='fcst-watersheds', name='Watersheds',  checked=True),
                                      dl.Overlay(fcst_points,           id='fcst-points',     name='Fcst Points', checked=True)])],
                   center=[38, -119], zoom=6,
                   style={'width': '100%', 'height': '100%', 'min-height': '800px', 'min-width': '800px', 'margin': '0px', 'display': 'block'})


## date picker
datepicker = html.Div(
    dcc.DatePickerSingle(
        id='datepicker',
        min_date_allowed=data_start.date(),
        max_date_allowed=data_end.date(),
        initial_visible_month=data_start.date(),
        date=curr_day.date()
    ),
    id='datepicker-container'
)

## day slider
day_marks = {}
for i in range(31):
    day_marks[i] = '%d' % (i+1)
    
slider_day =  html.Div(
    dcc.Slider(
        id='slider-day',
        min=0,
        max=30,
        step=1,
        marks=day_marks,
        value=curr_day.day-1
    ),
    id='slider-day-container'
)

## buttons for forward and backward moves
button_backward_day   = html.Button('<',  id='button-backward-day',   n_clicks=0)
button_backward_month = html.Button('<<', id='button-backward-month', n_clicks=0)
button_forward_day    = html.Button('>',  id='button-forward-day',    n_clicks=0)
button_forward_month  = html.Button('>>', id='button-forward-month',  n_clicks=0)

## figure title
title_var  = html.Div(var_longnames[0], id='title-var')
title_date = html.Div(curr_day.strftime(' @ %Y-%m-%d '), id='title-date')

title_zone = html.Div([title_var, title_date], id='title-zone')

## all date controls at the bottom
bottom_controls = html.Div([datepicker, button_backward_month, button_backward_day, slider_day, button_forward_day, button_forward_month, title_zone],
                           id='bottom-controls')

# some external things
external_stylesheets = ['https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css']
external_scripts     = ['https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js']  # js lib used for colors

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, prevent_initial_callbacks=True)

server = app.server

app.layout = html.Div([
    map_cnrfc,
    logo_cw3e,
    layer_var_select,
    bottom_controls
])

## Callbacks from here on

# callback to update data var in the title section
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_title_var'
    ),
    Output('title-var', 'children'),
    Input(component_id='dropdown-data', component_property='value')
)

# callback to update data date in the title section
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_title_date'
    ),
    Output('title-date', 'children'),
    Input('datepicker', 'date')
)

# callback to update url of image overlay
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_img_url'
    ),
    Output('data-img', 'url'),
    Input('datepicker', 'date'),
    Input(component_id='dropdown-data', component_property='value')
)

# callback to update url of color bar
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_cbar'
    ),
    Output('data-cbar-img', 'src'),
    Input(component_id='dropdown-data', component_property='value')
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_cbar_visibility'
    ),
    Output('data-cbar', 'href'),
    Input(component_id='data-map', component_property='checked')
)


# callback to update datepicker and slider on button clicks
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_date'
    ),
    Output(component_id='slider-day', component_property='value'),
    Output('datepicker', 'date'),
    Input('button-forward-day',  'n_clicks_timestamp'),
    Input('button-backward-day', 'n_clicks_timestamp'),
    Input('button-forward-month',   'n_clicks_timestamp'),
    Input('button-backward-month',  'n_clicks_timestamp'),
    Input(component_id='slider-day', component_property='value'),
    Input('datepicker', 'date'),
    Input('datepicker', 'min_date_allowed'),
    Input('datepicker', 'max_date_allowed')
)


if __name__ == '__main__':
    app.run_server(debug=True)
