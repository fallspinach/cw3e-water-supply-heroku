
// clientside callbacks for dash to eliminate unnecessary server-client communications and server load

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
    
        // update title variable name
        update_title_var: function(i_var) {
            var var_longnames = ['SWE Percentile', '2-m SM Percentile', 'Precipitation', 'Air Temperature', 'Monthly P Pctl', 'Monthly T Pctl'];
            return var_longnames[i_var];
        },
        
        // update title date
        update_title_date: function(date_value) {
            return ' @ ' + date_value;
        },
        
        // update title date
        update_title_hour: function(hour_value) {
            if (hour_value<10) {
                return '0' + hour_value + ':00Z';
            } else {
                return hour_value + ':00Z';
            }
        },
        
        // update overlay image url
        update_img_url: function(date_value, var_value) {
            var base_url = 'https://cw3e.ucsd.edu/wrf_hydro/cnrfc/imgs/monitor/';
            var var_names = ['swe_r', 'smtot_r', 'precip', 'tair2m', 'precip_r', 'tair2m_r'];
            var var_types = ['output', 'output', 'forcing', 'forcing', 'forcing', 'forcing'];
            var d = new Date(date_value);
            var yyyy = d.getUTCFullYear().toString();
            var mm = (d.getUTCMonth()+1).toString(); if (mm<10) { mm = '0' + mm; }
            var dd = d.getUTCDate().toString(); if (dd<10) { dd = '0' + dd; }
            if (var_names[var_value]=='precip_r' || var_names[var_value]=='tair2m_r') {
                dd = ''
            }
            var new_url = base_url + var_types[var_value] + '/' + yyyy + '/' + var_names[var_value] + '_' + yyyy + mm + dd + '.png';
            return new_url;
        },
        
        // update overlay color bar
        update_cbar: function(var_value) {
            var base_url = 'https://cw3e.ucsd.edu/wrf_hydro/cnrfc/imgs/monitor/';
            var var_names = ['swe_r', 'smtot_r', 'precip', 'tair2m', 'precip_r', 'tair2m_r'];
            var var_types = ['output', 'output', 'forcing', 'forcing', 'forcing', 'forcing'];
            var new_url = base_url + var_types[var_value] + '/' + var_names[var_value] + '_cbar.png';
            return new_url;
        },
        
        update_cbar_visibility: function(checked) {
            if (checked>0) {
                return {'display': 'none'};
            }
            else {
                return {'display': 'block'};
            }
        },

        // update datepicker and slider on button clicks
        update_date: function(dfwd_t, dbwd_t, mfwd_t, mbwd_t, d_slide, d_old, d_min, d_max) {
        
            var date_old = new Date(d_old);
            
            var date_min =new Date(d_min);
            var date_max =new Date(d_max);
            
            var date_new = new Date();
            
            if (dfwd_t==null) { dfwd_t = 0; }
            if (dbwd_t==null) { dbwd_t = 0; }
            if (mfwd_t==null) { mfwd_t = 0; }
            if (mbwd_t==null) { mbwd_t = 0; }
            
            if (dfwd_t>dbwd_t && dfwd_t>mfwd_t && dfwd_t>mbwd_t) {
                // forward-day
                date_new.setTime(date_old.getTime() + 3600*1000*24);
            }
            else if (dbwd_t>dfwd_t && dbwd_t>mfwd_t && dbwd_t>mbwd_t) {
                // backward-day
                date_new.setTime(date_old.getTime() - 3600*1000*24);
            }
            else if (mfwd_t>dfwd_t && mfwd_t>dbwd_t && mfwd_t>mbwd_t) {
                // forward-month
                date_new.setTime(date_old.getTime() + 24*3600*1000*30.4375);
            }
            else if (mbwd_t>dfwd_t && mbwd_t>dbwd_t && mbwd_t>mfwd_t) {
                // backward-day
                date_new.setTime(date_old.getTime() - 24*3600*1000*30.4375);
            }
            else {
                date_new.setTime(date_old.getTime());
            }
            
            var timenow = Date.now();
            if (timenow-dfwd_t>100 && timenow-dbwd_t>100 && timenow-mfwd_t>100 && timenow-mbwd_t>100) {
                date_new.setTime(date_old.getTime());
            }
            
            if (date_new.getTime()<date_min.getTime()) {
                date_new = date_min;
            }
            if (date_new.getTime()>date_max.getTime()) {
                date_new = date_max;
            }
            
            return [date_new.getUTCDate()-1, date_new.toISOString().split('T')[0]];
            
        },
        
        // toggle forcing map
        toggle_forcing_map: function(selected) {
            if (selected=='forcing') {
                return [true, false, {'display': 'inline-block'}];
            } else {
                return [false, true, {'display': 'none'}];
            }
        },
        
        // toggle gauge map
        toggle_gauge_map: function(layer_selected, gauge_selected) {
            if (layer_selected=='gauges') {
                if (gauge_selected=='usgs') {
                    return [true, false, false];
                } else {
                    return [false, true, false];
                }
            } else {
                return [false, false, true];
            }
        },
        
        // close popup window
        popup_close: function(n_clicks) {
            if (n_clicks>0) {
                return {'display': 'none'};
            } else {
                return {'display': 'block'};
            }
        },
        
        // open popup window
        popup_open: function(n_clicks_timestamp_x, fcst_point) {
            var timenow = Date.now();
            if (timenow-n_clicks_timestamp_x<100) {
                return [{'display': 'none'}, 'Station not selected yet'];
            } else {
                title = fcst_point['properties']['tooltip'];
                return [{'display': 'block'}, title];
            }
        },
        
        // reset click_features
        reset_click_feature: function(gauge_selected) {
            return [null, null];
        }
        
    }
});
