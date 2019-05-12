
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

app.secret_key = '184963b1-c23a-4b30-845d-073bfe3210f0'


@app.route('/')
def main():
    return render_template('main.html')
