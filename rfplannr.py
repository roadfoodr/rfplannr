from flask import Flask, render_template, g
import os
import sqlite3
from hashids import Hashids
from flask_table import Col, create_table

app = Flask(__name__)
app.app_context().push()
app.secret_key = os.environ.get('SECRET_KEY', 'dev')
GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', 'dev')
@app.context_processor
def inject_global_vars():
    return {'GA_TRACKING_ID': GA_TRACKING_ID}
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True

# STATES = ['VA', 'NC', 'TN', 'SC', 'GA', 'AL', 'MS', 'LA']
# STATES = ['OK', 'TX', 'NM']
STATES = []  # null list to select everything

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


@app.route('/')
def root(limit=None, hashid=None):    
    items = get_rows(STATES, limit, hashid)  
    markers = [{
                'ID': item['ID'],
                'lat': item['lat'],
                'lon': item['long'],
                'popup': f"<strong>{item['Restaurant']}</strong>"
                         f"<br>{item['City']}, {item['State']}"
                         f"{'<br><em>Roadfood Honor Roll</em>' if item['Honor Roll'] == 'y' else ''}",
                'color': "'green'" if item['Checkmark'] == 'y' else "'royalblue'",
                'honor-roll': item['Honor Roll']
                } for item in items if item['lat'] and item['Crossout'] != 'y']
    
    return render_template('map.html', markers=markers)

@app.route('/<string:hashid>')
def recall_selection(hashid):
    return root(limit=None, hashid=hashid)

@app.route('/export/<string:hashid>')
def export_selection(hashid):   
    export_cols = ['Restaurant', 'City', 'State', 'Address', 'Honor Roll', 'Notes']

    ItemTable = create_table('ItemTable')
    for col_name in export_cols:
        ItemTable.add_column(col_name, Col(col_name))

    items = get_rows(limit=None, hashid=hashid) 
    table = ItemTable(items, table_id='data', 
                      classes=['table', 'table-striped'],
                      thead_classes=['thead-dark'])

    return render_template("table_view.html", hashid=hashid, table=table)


