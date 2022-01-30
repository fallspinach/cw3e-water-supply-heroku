import os

import dash
from dash import html

from components import map_cnrfc, logo_cw3e, layer_var_select, popup_window, bottom_controls


# some external things
external_stylesheets = ['https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css']
external_scripts     = ['https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js']  # js lib used for colors

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, prevent_initial_callbacks=True)

server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Water Supply Forecast (experimental & internal use only)</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    map_cnrfc,
    logo_cw3e,
    layer_var_select,
    popup_window,
    bottom_controls
])

from callbacks import *
    
if __name__ == '__main__':
    app.run_server(debug=True)
