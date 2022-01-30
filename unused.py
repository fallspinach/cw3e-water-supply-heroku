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



