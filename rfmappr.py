from flask import Flask, render_template
import os, random

app = Flask(__name__)
app.app_context().push()
app.secret_key = os.environ.get('SECRET_KEY', 'dev')
GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', 'dev')
@app.context_processor
def inject_global_vars():
    return {'GA_TRACKING_ID': GA_TRACKING_ID}


@app.route('/')
def root():
    # markers=[
    #     {
    #     'lat':39.8283,
    #     'lon':-98.5795,
    #     'popup':'This is the middle of the map.'
    #     }
    # ]
    
    top, bottom, left, right = 49.382808, 24.521208, -66.945392, -124.736342

    markers = [{
                'lat': random.uniform(bottom, top),
                'lon': random.uniform(left, right),
                'popup': 'This is a marker.'
                } for _ in range(1000)]
    
    
    return render_template('index.html', markers=markers)
