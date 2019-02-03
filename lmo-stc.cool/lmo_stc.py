
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

app.secret_key = '184963b1-c23a-4b30-845d-073bfe3210f0'


@app.route('/')
def temporary_landing_page():
    return render_template('temporary_landing_page.html')


@app.route('/why_maine')
def why_maine():
    return render_template('why_maine.html')


@app.route('/accommodations')
def accommodations():
    return render_template('accommodations.html')


@app.route('/getting_there')
def getting_there():
    return render_template('getting_there.html')


@app.route('/details_etc')
def details_etc():
    return render_template('details_etc.html')


@app.route('/fbc05915-e73b-4f3c-8a05-92ad888ee76e')
def alt():
    return render_template('alt.html')