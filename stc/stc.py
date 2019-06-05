
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from credentials import secret_key


app = Flask(__name__)
Bootstrap(app)

app.secret_key = secret_key

@app.route('/')
def main():
    return render_template('main.html')
