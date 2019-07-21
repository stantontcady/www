

from flask import Flask, render_template

from credentials import secret_key


app = Flask(__name__)




@app.route('/daily_photo_grid')
def daily_photo_grid():
    return render_template('daily_photo_grid.html')
