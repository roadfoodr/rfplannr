from flask import Flask, g, redirect, render_template, request, url_for, send_file
import os
import sqlite3
import sys
import re
import urllib.parse as urlparse
from hashids import Hashids
from flask_table import Col, create_table
from xlsxwriter.workbook import Workbook
from io import BytesIO
from datetime import date


app = Flask(__name__)
app.app_context().push()
# app.secret_key = os.environ.get('SECRET_KEY', 'dev')
GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', 'dev')
@app.context_processor
def inject_global_vars():
    return {'GA_TRACKING_ID': GA_TRACKING_ID}
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True

FILE_BASE = 'rfplannr'
DB_NAME = 'roadfood'
DATABASE = os.path.join(app.root_path, 'data', f'{FILE_BASE}.sqlite')

hashids = Hashids(salt='', min_length=0)

#%% Utility functions
def make_hashid(ids):
    hashid = hashids.encode(*ids)
    return hashid

def decode_hashid(hashid):
    ids = hashids.decode(hashid)
    return ids

#%% DB handling

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # return rows as dicts (allows access of fields via keys)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = g.get('_database', None)
    if db is not None:
        db.close()


def get_rows(states=None, limit=None, hashid=None):
    states = [] if states is None else states
    limit_str = f' LIMIT {limit}' if limit else ''
    cols = ['ID', 'Restaurant', 'City', 'State', 'Address', 'Checkmark', 
            'lat', 'long', 'Crossout', '"Honor Roll"', 'Notes']
    col_string = ', '.join(cols)
    # expand the necessary number of qmarks, or use the column name to get all
    state_qmarks = f"({', '.join('?' for _ in states)})" if states else '(State)'
    ids = decode_hashid(hashid)
    ids_qmarks = f"({', '.join('?' for _ in ids)})" if ids else '(ID)'
    
    sql = f'SELECT {col_string} FROM {DB_NAME} ' \
          f'WHERE State IN {state_qmarks} ' \
          f'AND ID IN {ids_qmarks}' \
          f'{limit_str}'
          
    cursor = get_db().cursor()   
    cursor.execute(sql, list(states)+list(ids))
    items = cursor.fetchall()
    return items

def get_states(hashid=None):
    ids = decode_hashid(hashid)
    ids_qmarks = f"({', '.join('?' for _ in ids)})" if ids else '(ID)'

    sql = f'SELECT DISTINCT State FROM {DB_NAME} ' \
          f'WHERE ID IN {ids_qmarks}' \

    cursor = get_db().cursor()
    cursor.execute(sql, list(ids))
    items = cursor.fetchall()
    distinct_states = sorted([item['State'] for item in items])
    return distinct_states


#%% Routes

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/map', methods=['GET'])
def root(states=None, limit=None, hashid=None):
    items = get_rows(states, limit, hashid)
    goog_prefix = 'https://google.com/search?q='
    markers = [{
                'ID': item['ID'],
                'lat': item['lat'],
                'lon': item['long'],
                'popup': f"<a href='{goog_prefix}{urlparse.quote_plus(item['Restaurant'])}"
                         f"+{urlparse.quote_plus(item['City'])}"
                         f"+{urlparse.quote_plus(item['State'])}"
                         f"' target='_blank'>"
                         f"<strong>{item['Restaurant']}</strong>"
                         f"</a>"
                         f"<br>{item['City']}, {item['State']}"
                         f"{'<br><em>Roadfood Honor Roll</em>' if item['Honor Roll'] == 'y' else ''}",
                'color': "'green'" if item['Checkmark'] == 'y' else "'royalblue'",
                'honor-roll': item['Honor Roll']
                } for item in items if item['lat'] and item['Crossout'] != 'y']
    return render_template('map.html', markers=markers)

@app.route('/map', methods=['POST'])
def filter_states():
    state_string = request.form['submit-states'].upper()
    states = re.split('[^A-Z]', state_string)
    states = list(filter(None, states))
    return root(states=states)

@app.route('/map')
def recall_selection_all(hashid='ALL'):
    return recall_selection(hashid)
@app.route('/map/<string:hashid>')
def recall_selection(hashid=''):
    return root(states=None, limit=None, hashid=hashid)

@app.route('/table')
def table_selection_all(hashid='ALL'):
    return table_selection(hashid)
@app.route('/table/<string:hashid>')
def table_selection(hashid=''):
    table_cols = ['Restaurant', 'City', 'State', 'Address', 'Honor Roll', 'Notes']

    ItemTable = create_table('ItemTable')
    for col_name in table_cols:
        ItemTable.add_column(col_name, Col(col_name))

    items = get_rows(limit=None, hashid=hashid) 
    table = ItemTable(items, table_id='data', 
                      classes=['table', 'table-striped'],
                      thead_classes=['thead-dark'])

    return render_template("table_view.html", hashid=hashid, table=table)

@app.route('/export')
def export_selection_all(hashid='ALL'):   
    return export_selection(hashid)
@app.route('/export/<string:hashid>')
def export_selection(hashid=''):
    export_cols = ['Restaurant', 'City', 'State', 'Address', 'Honor Roll', 'Notes']
    export_col_widths = [35, 15, 6, 25, 10, 40]

    items = get_rows(limit=None, hashid=hashid)

    output = BytesIO()
    workbook = Workbook(output)
    # workbook.formats[0].font_name = 'Verdana'
    # workbook.formats[0].font_size = 10

    worksheet = workbook.add_worksheet('Locations')
    # Add header row to workbook
    format_bold = workbook.add_format({'bold': True})
    for j, colname in enumerate(export_cols):
        worksheet.write(0, j, colname, format_bold)
        worksheet.set_column(j, j, export_col_widths[j])

    header_offset = 1
    for i, row in enumerate(items):
        for j, colname in enumerate(export_cols):
            worksheet.write(i+header_offset, j, row[colname])

    hashid = 'ALL' if not hashid else hashid
    worksheet = workbook.add_worksheet('Permalinks')
    worksheet.write(0, 0, "Permalink to map view for this selection:")
    worksheet.write(1, 0, url_for('recall_selection', hashid=hashid, _external=True))       
    worksheet.write(3, 0, "Permalink to table view for this selection:")
    worksheet.write(4, 0, url_for('table_selection', hashid=hashid, _external=True))

    workbook.close()
    output.seek(0)

    # generate filename including date and states
    date_string = date.today().strftime('%m%d%y')

    all_states = get_states('')
    distinct_states = get_states(hashid)
    if len(distinct_states) == len(all_states):
        states_string = 'ALL'
    else:
        max_filename_states = 5
        states_string_suffix = ''
        if len(distinct_states) > max_filename_states:
            states_string_suffix = '-plus'
            distinct_states = distinct_states[:max_filename_states]
        states_string = "-".join(distinct_states) + states_string_suffix
    
    return send_file(output,
                     attachment_filename=f'Roadfood_{date_string}-{states_string}.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True)

@app.errorhandler(404)
def invalid_route(e):
    return redirect(url_for('home_page'))

