from flask import current_app as app, render_template
from bs4 import BeautifulSoup
from requests import post
from json import loads

url = 'http://127.0.0.1:80/api'

with open('interface/templates/dash_raw.html', 'r') as file:
    dash_index = file.read()

@app.route('/live-chart')
def chart():
    soup = BeautifulSoup(dash_index)
    return render_template('live_chart.html', title='Qraxiss Trade', footer=soup.footer)
