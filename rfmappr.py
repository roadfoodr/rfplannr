from flask import Flask, render_template, g
import os
import sqlite3
from hashids import Hashids

app = Flask(__name__)
app.app_context().push()
app.secret_key = os.environ.get('SECRET_KEY', 'dev')
GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', 'dev')
@app.context_processor
def inject_global_vars():
    return {'GA_TRACKING_ID': GA_TRACKING_ID}

# STATES = ['VA', 'NC', 'TN', 'SC', 'GA', 'AL', 'MS', 'LA']
# STATES = ['OK', 'TX']
STATES = []  # null list to select everything

FILE_BASE = 'Roadfood_MDP_041622_GEO'
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


def get_rows(limit=None, hashid=None):
    limit_str = f' LIMIT {limit}' if limit else ''
    cols = ['ID', 'Restaurant', 'Checkmark', 'lat', 'long', 'Crossout']
    col_string = ', '.join(cols)
    # expand the necessary number of qmarks, or use the column name to get all
    state_qmarks = f"({', '.join('?' for _ in STATES)})" if STATES else '(State)'
    ids = decode_hashid(hashid)
    ids_qmarks = f"({', '.join('?' for _ in ids)})" if ids else '(ID)'
    
    sql = f'SELECT {col_string} FROM {DB_NAME} ' \
          f'WHERE State IN {state_qmarks} ' \
          f'AND ID IN {ids_qmarks}' \
          f'{limit_str}'

    cursor = get_db().cursor()   
    cursor.execute(sql, list(STATES)+list(ids))
    items = cursor.fetchall()
    return items


@app.route('/')
def root(limit=None, hashid=None):    
    items = get_rows(limit, hashid)  
    markers = [{
                'ID': item['ID'],
                'lat': item['lat'],
                'lon': item['long'],
                'popup': item['Restaurant'],
                'color': "'green'" if item['Checkmark'] == 'y' else "'royalblue'"
                } for item in items if item['lat'] and item['Crossout'] != 'y']
    
    return render_template('index.html', markers=markers)

@app.route('/<string:hashid>')
def recall_selection(hashid):
    return root(limit=None, hashid=hashid)

@app.route('/export/<string:hashid>')
def export_selection(hashid):
    return hashid


