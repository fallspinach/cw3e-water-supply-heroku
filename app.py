import os

import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import ClientsideFunction, Input, Output
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import Namespace, arrow_function, assign

import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta

# temporary set up
curr_day   = (datetime.utcnow()-timedelta(days=1, hours=10)).date()
data_start = date(2021, 7, 1)
data_end   = curr_day


## data variable selection dropdown
var_longnames = ['SWE Percentile', '2-m SM Percentile', 'Precipitation', 'Air Temperature']
var_names = ['swe_r', 'smtot_r', 'precip', 'tair2m']

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

fcst_points = dl.GeoJSON(url='assets/fnf_points_proj_tooltip.pbf', format='geobuf', id='fcst-points',
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
img_url = base_url + curr_day.strftime('monitor/output/%Y/'+ var_names[0] + '_%Y%m%d.png')
data_map = dl.ImageOverlay(id='data-img', url=img_url, bounds=cnrfc_domain, opacity=0.7)

# color bar
data_cbar = html.A(html.Img(src=base_url+'monitor/output/'+ var_names[0] + '_cbar.png', title='Color Bar', id='data-cbar-img'), id='data-cbar')


## all layers
locator = dl.LocateControl(options={'locateOptions': {'enableHighAccuracy': True}})
maptile = dl.TileLayer(url='http://services.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}')
map_cnrfc = dl.Map([maptile, locator,
                    dl.LayersControl([dl.Overlay([data_map, data_cbar], id='data-map-ol',        name='Data',        checked=True),
                                      dl.Overlay(cnrfc_boundary,        id='cnrfc-boundary-ol',  name='CNRFC',       checked=True),
                                      dl.Overlay(fcst_watersheds,       id='fcst-watersheds-ol', name='Watersheds',  checked=True),
                                      dl.Overlay(fcst_points,           id='fcst-points-ol',     name='Fcst Points', checked=True)])],
                   center=[38, -119], zoom=6,
                   style={'width': '100%', 'height': '100%', 'min-height': '800px', 'min-width': '800px', 'margin': '0px', 'display': 'block'})


## date picker
datepicker = html.Div(
    dcc.DatePickerSingle(
        id='datepicker',
        min_date_allowed=data_start,
        max_date_allowed=data_end,
        initial_visible_month=data_start,
        date=curr_day
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

## build time series figures

fnf_stations = ['AMF', 'CSN', 'EFC', 'EWR', 'FTO', 'KGF', 'KRI', 'KWT', 'MKM', 'MRC', 'MSS', 'PSH', 'SBB', 'SCC', 'SDT', 'SIS', 'SJF', 'SNS', 'TLG', 'TNL', 'TRF', 'WFC', 'WWR', 'YRS']

# flow reanalysis figure
def draw_reana(staid):
    if staid in fnf_stations:
        fcsv = 'assets/reanalysis/%s.csv' % staid
        df = pd.read_csv(fcsv, parse_dates=True, index_col='Date', names=['Date', 'FNF', 'Qsim', 'QsimBC'])
        fig_reana = px.line(df, labels={'Date': '', 'value': 'Flow (kaf/mon)'})
    else:
        fig_reana = px.line(x=[2018, 2023], y=[0, 0], labels={'x': 'Data not available.', 'y': 'Flow (kaf/mon)'})
    fig_reana.update_layout(margin=dict(l=15, r=15, t=15, b=5))
    return fig_reana
    
# flow monitor/forecast figure
def draw_mofor(staid):
    if staid in fnf_stations:
        fcsv = 'assets/forecast/%s_20220101-20220731.csv' % staid
        df = pd.read_csv(fcsv, parse_dates=True, index_col='Date', usecols = ['Date']+['Ens%02d' % (i+1) for i in range(42)]+['Avg', 'Exc50', 'Exc90', 'Exc10'])
        linecolors = {'Ens%02d' % (i+1): 'lightgray' for i in range(42)}
        linecolors.update({'Avg': 'black', 'Exc50': 'green', 'Exc90': 'red', 'Exc10': 'blue'})
        fig_mofor = px.line(df, labels={'Date': '', 'value': 'Flow (kaf/mon)'}, color_discrete_map=linecolors, markers=True)
    else:
        fig_mofor = px.line(x=[2018, 2023], y=[0, 0], labels={'x': 'Data not available.', 'y': 'Flow (kaf/mon)'})
    fig_mofor.update_layout(margin=dict(l=15, r=15, t=15, b=5))
    return fig_mofor
    
# ancillary data figure
def draw_ancil(staid):
    if staid!=None:
        fig_ancil = px.line(x=[2018, 2023], y=[50, 50], labels={'x': 'Time', 'y': 'Percentile'})
    else:
        fig_ancil = px.line(x=[2018, 2023], y=[50, 50], labels={'x': 'Data not available.', 'y': 'Percentile'})
    return fig_ancil

# forecast table
def draw_table(staid):
    cols = ['Date', 'Exc50', 'Pav50', 'Exc90', 'Pav90', 'Exc10', 'Pav10', 'Avg']
    if staid in fnf_stations:
        fcsv = 'assets/forecast/%s_20220101-20220731.csv' % staid
        df = pd.read_csv(fcsv, parse_dates=False, usecols=cols)
        df = df[cols]
        cols.remove('Date')
        df[cols] = np.rint(df[cols])
        df['Date'] = [ datetime.strptime(m, '%Y-%m-%d').strftime('%B %Y') for m in df['Date'] ]
    else:
        fcsv = 'assets/forecast/FTO_20220101-20220731.csv'
        df = pd.read_csv(fcsv, parse_dates=False, usecols=cols)
        df = df[cols]
        df.drop(df.index, inplace=True)

    df.rename(columns={'Date': 'Month', 'Exc50': '50% (KAF)', 'Pav50': '50% (%AVG)', 'Exc90': '90% (KAF)', 'Pav90': '90% (%AVG)', 'Exc10': '10% (KAF)', 'Pav10': '10% (%AVG)', 'Avg': 'AVG (KAF)'}, inplace=True)
    table_fcst = dash_table.DataTable(id='fcst-table',
                                      columns=[{'name': i, 'id': i} for i in df.columns],
                                      data=df.to_dict('records'),
                                      style_header={'backgroundColor': 'lightyellow', 'fontWeight': 'bold'},
                                     )
    return table_fcst

fig_reana = draw_reana('FTO')
fig_mofor = draw_mofor('FTO')
fig_ancil = draw_ancil('FTO')

table_fcst = draw_table('FTO')
table_note = html.Div('[Note] 50%, 90%, 10%: exceedance levels within the forecast ensemble. AVG: month of year average during 1979-2020. %AVG: percentage of AVG. KAF: kilo-acre-feet.', id='table-note')

## pop-up window

graph_reana = dcc.Graph(id='graph-reana', figure=fig_reana, style={'height': '360px'})
graph_mofor = dcc.Graph(id='graph-mofor', figure=fig_mofor, style={'height': '360px'})
graph_ancil = dcc.Graph(id='graph-ancil', figure=fig_ancil, style={'height': '360px'})
div_table = html.Div(id='div-table', children=[table_fcst, table_note], style={'padding': '20px'})

tab_style = {'height': '28px', 'padding': '1px', 'margin': '0px'}

tab_reana = dcc.Tab(label='Reanalysis',      value='reana', children=[dcc.Loading(id='loading-reana', children=graph_reana)], style=tab_style, selected_style=tab_style)
tab_mofor = dcc.Tab(label='Monitor/Forecast',value='mofor', children=[dcc.Loading(id='loading-mofor', children=graph_mofor)], style=tab_style, selected_style=tab_style)
tab_ancil = dcc.Tab(label='Ancillary Data',  value='ancil', children=[dcc.Loading(id='loading-ancil', children=graph_ancil)], style=tab_style, selected_style=tab_style)
tab_table = dcc.Tab(label='Table',           value='table', children=[dcc.Loading(id='loading-table', children=div_table)],  style=tab_style, selected_style=tab_style)

button_popup_close = html.Button(' X ', id='button-popup-close')
title_popup = html.Div('B-120 Forecast Point', id='title-popup')

popup_tabs = dcc.Tabs([tab_reana, tab_mofor, tab_ancil, tab_table], id='popup-tabs', value='reana', style=tab_style)

# popup window for time series
popup_window = html.Div([title_popup, button_popup_close, popup_tabs], id='popup-window', style={'display': 'none', 'height': '450px'})


# some external things
external_stylesheets = ['https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css']
external_scripts     = ['https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js']  # js lib used for colors

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, prevent_initial_callbacks=True)

server = app.server

app.layout = html.Div([
    map_cnrfc,
    logo_cw3e,
    layer_var_select,
    popup_window,
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
    Output('data-cbar', 'style'),
    Input(component_id='data-map-ol', component_property='checked')
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

# callback to popup time seris window upon feature click
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='popup_open'
    ),
    Output('popup-window', 'style'),
    Output('title-popup', 'children'),
    Input('button-popup-close',  'n_clicks_timestamp'),
    Input('fcst-points', 'click_feature'),
)

# create/update historic time series graph in popup
@app.callback(Output(component_id='graph-reana', component_property='figure'),
              Output(component_id='graph-mofor', component_property='figure'),
              Output(component_id='div-table', component_property='children'),
              Input('fcst-points', 'click_feature'))
def update_flows(fcst_point):

    fig_reana = draw_reana(fcst_point['properties']['Station_ID'])
    fig_mofor = draw_mofor(fcst_point['properties']['Station_ID'])
    table_fcst = draw_table(fcst_point['properties']['Station_ID'])
            
    return [fig_reana, fig_mofor, [table_fcst, table_note]]

if __name__ == '__main__':
    app.run_server(debug=True)
