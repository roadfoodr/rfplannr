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

REGIONS = ['VA', 'NC', 'TN', 'SC', 'GA', 'AL', 'MS', 'LA']
FILE_BASE = 'Roadfood_MDP_041122_GEO'
DB_NAME = 'roadfood'
DATABASE = os.path.join(app.root_path, 'data', f'{FILE_BASE}.sqlite')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
    
    cursor = get_db().cursor()
    cursor.execute(f'SELECT {col_string} FROM {DB_NAME}{limit_str}')
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
                'lat': item[2],
                'lon': item[3],
                'popup': item[0],
                'color': "'green'" if item[1] == 'y' else "'royalblue'"
                } for item in items if item[2] and item[4] != 'y']
    
    return render_template('index.html', markers=markers)
