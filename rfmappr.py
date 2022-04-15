from flask import Flask, render_template, g
import os
import sqlite3

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

FILE_BASE = 'Roadfood_MDP_041122_GEO'
DB_NAME = 'roadfood'
DATABASE = os.path.join(app.root_path, 'data', f'{FILE_BASE}.sqlite')


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


def get_rows(limit=None):
    limit_str = f' LIMIT {limit}' if limit else ''
    cols = ['Restaurant', 'Checkmark', 'lat', 'long', 'Crossout']
    col_string = ', '.join(cols)
    # expand the necessary number of qmarks, or use the column name to get all
    state_qmarks = f"({', '.join('?' for _ in STATES)})" if STATES else '(State)'
   
    sql = f'SELECT {col_string} FROM {DB_NAME} ' \
          f'WHERE State IN {state_qmarks}' \
          f'{limit_str}'
    
    cursor = get_db().cursor()   
    cursor.execute(sql, STATES)
    items = cursor.fetchall()
    return items


@app.route('/')
def root():
    # markers=[
    #     {
    #     'lat':39.8283,
    #     'lon':-98.5795,
    #     'popup':'This is the middle of the map.'
    #     }
    # ]
    
    items = get_rows()  
    markers = [{
                'lat': item['lat'],
                'lon': item['long'],
                'popup': item['Restaurant'],
                'color': "'green'" if item['Checkmark'] == 'y' else "'royalblue'"
                } for item in items if item['lat'] and item['Crossout'] != 'y']
    
    return render_template('index.html', markers=markers)
