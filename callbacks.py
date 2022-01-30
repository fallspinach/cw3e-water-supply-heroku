from app import app
from plots import *

from dash.dependencies import ClientsideFunction, Input, Output

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
    if fcst_point==None:
        staid = 'FTO'
    else:
        staid = fcst_point['properties']['Station_ID']
    fig_reana = draw_reana(staid)
    fig_mofor = draw_mofor(staid)
    if staid!='SRS':
        table_fcst = draw_table(staid, all_stations[staid])
    else:
        table_fcst = draw_table_all()
    
    #return [fig_reana, fig_mofor, [table_fcst, table_note]]
    return [fig_reana, fig_mofor, table_fcst]
    

