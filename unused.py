# forecast tables over all FNF stations
def draw_table_all():
    table_fcst_all = []
    for staid,staname in fnf_id_names.items():
    	table_fcst_all.append(draw_table(staid, staname)[0])
    table_fcst_all.append(table_note)
    return table_fcst_all


## failed attempt to print the table tab

button_print = html.Button(id='button-print', children='Print Table')
img_div = html.Div(id='img-div')
table_note = html.Div([button_print, '  [Note] 50%, 90%, 10%: exceedance levels within the forecast ensemble. AVG: month of year average during 1979-2020. %AVG: percentage of AVG. KAF: kilo-acre-feet.', img_div], id='table-note')


# print tables in PDF
app.clientside_callback(
    '''
    function (n_clicks) {
        if (n_clicks > 0) {
            html2canvas(document.getElementById('div-table')).then(function(canvas) {
                var img = new Image();
                var height = canvas.height;
                img.src = canvas.toDataURL("image/png");
                document.getElementById('img-div').appendChild(img);

                var doc = new PDFDocument({layout:'portrait', margin: 25});
                var stream = doc.pipe(blobStream());

                var img_container = document.getElementById('img-div');
                var imgElement = img_container.getElementsByTagName('img');
                var imgSrc = imgElement[imgElement.length - 1].src;
                doc.image(imgSrc, {width: 600});

                doc.end();

                var saveData = (function () {
                    var a = document.createElement("a");
                    document.body.appendChild(a);
                    a.style = "display: none";
                    return function (blob, fileName) {
                        var url = window.URL.createObjectURL(blob);
                        a.href = url;
                        a.download = fileName;
                        a.click();
                        window.URL.revokeObjectURL(url);
                    };
                }());

                stream.on('finish', function() {
                  var blob = stream.toBlob('application/pdf');
                  saveData(blob, 'forecast_table.pdf');
                });
            });


        }
        return false;
    }
    ''',
    Output('button-print', 'disabled'),
    [
        Input('button-print', 'n_clicks'),
    ]
)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Water Supply Forecast (experimental & internal use only)</title>
        {%favicon%}
        {%css%}
    </head>
    <body style="width: 100%; background-color: #eaeaea;">
      <div style="width: 1368px; margin-left: auto; margin-right: auto;">
        <header><div><a href="https://cw3e.ucsd.edu/"><img src="https://cw3e.ucsd.edu/wp-content/uploads/2017/03/header_finalv2.png"></a></div></header>
        {%app_entry%}
        <footer style="background-color: #1e6b8b;">
            <table width="100%" style="padding-top:0px; padding-left: 20px; padding-right:20px; padding-bottom:0px; border: 0; margin-bottom: 0px;"><tr>
<td width="6%" valign="top" align="center" style="border: 0; padding-top: 25px; padding-bottom:0px; margin-bottom: 0px;"><center><a href="https://cw3e.ucsd.edu/"><img src="https://cw3e.ucsd.edu/images/cw3e_logo_files/wetransfer-b4ff74/CW3E%20Final%20Logo%20Suite/5-Vertical-Acronym%20Onlhy/Digital/PNG/CW3E-Logo-Vertical-Acronym-White.png" width="75%"></a></center></td>
<td width="33%" valign="top" style="border: 0; padding-top: 20px; padding-bottom:0px; margin-bottom: 0px;"><p id="footer_titles"><b>F. Martin Ralph, PhD., Director</b></p><p class="nowrap" id="footer_text"><b>Center For Western Weather and Water Extremes (CW3E)</b><br>Scripps Institution of Oceanography<br>University of California, San Diego<br>9500 Gilman Drive</span><br>La Jolla, CA 92093<br><a href="https://cw3e.ucsd.edu/cw3e_location/" style="color:#000">Directions</a></p><br></td>
<td width="24%" valign="top" style="border: 0; padding-top:20px; padding-bottom:0px; margin-bottom: 0px;"><p id="footer_titles"><b>CW3E Partners</b></p><p class="nowrap" id="footer_text"><a href="http://www.water.ca.gov/" style="color:#fff" target="_blank">California Department of Water Resources</a><br><a href="http://www.noaa.gov/" style="color:#fff" target="_blank">NOAA National Weather Service</a><br><a href="https://www.jpl.nasa.gov/" style="color:#fff" target="_blank">NASA/Jet Propulsion Laboratory</a><br><a href="http://www.ocwd.com" style="color:#fff" target="_blank">Orange County Water District</a><br><a href="http://www.scwa.ca.gov/" style="color:#fff" target="_blank">Sonoma Water</a><br><a href="http://www.usace.army.mil/" style="color:#fff" target="_blank">U.S. Army Corps of Engineers</a><br><a href="https://www.usbr.gov/" style="color:#fff" target="_blank">U.S. Bureau of Reclamation</a></p><br></td>
<td width="23%" valign="top" style="border: 0; padding-right: 20px; padding-top: 20px; padding-bottom:0px;"><p id="footer_titles"><b>Search CW3E</b></p>
<form role="search" method="get" class="search-form" action="https://cw3e.ucsd.edu/">
	<label>
		<span class="screen-reader-text">Search for:</span>
		<input type="search" class="search-field" placeholder="Search &hellip;" value="" name="s" />
	</label>
	<button type="submit" class="search-submit"><span class="screen-reader-text">Search</span></button>
</form>

  <table style="padding-bottom: 0px; border: 0">
    <tr><td style="border: 0; padding-bottom: 0px;"><p class="nowrap" id="footer_text" align="left"><a href="https://cw3e.ucsd.edu/disclaimer/" style="color:#fff">Disclaimer</a></p></td><td style="border: 0; padding-bottom: 0px; margin-bottom: 0px;"><p class="nowrap" id="footer_text" align="right"><a href="mailto:cw3e-website-g@ucsd.edu"  style="color:#fff">Contact Webmaster</p></td></tr>
    <tr><td colspan="2" style="border: 0; padding-bottom: 0px;"><a href="https://twitter.com/CW3E_Scripps" style="color:#fff" target="_blank"><img id="twitter_logo" class="twitter_logo" src="https://cw3e.ucsd.edu/images/other/twitter-icon.png" align="left" style="width: 26px; height: 26px"><p class="nowrap" id="footer_titles" align="left" style="padding-top:15px;">Follow CW3E on Twitter</a></p></td></tr>
  </table><center> <img src="https://cw3e.ucsd.edu/images/logos/UCSD_SIO.png" style="margin-top: -20px; margin-bottom: 10px;" width="80%"></center>  </td></tr>
            </table>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
      </div>
    </body>
</html>
'''


