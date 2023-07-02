from flask import Flask, render_template, request
import os
import json
import secrets
import requests
import numpy as np
import json
from forms import SearchForm
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, timedelta

app = Flask(__name__)

app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config['SECRET_KEY'] = secrets.token_hex()

@app.route('/',methods = ['GET','POST'])
def send():

    form = SearchForm()

    if form.validate_on_submit():
        LOCATION = form.LOCATION.data
        START_DATE = form.START_DATE.data
        END_DATE = form.END_DATE.data
        API_KEY = form.API_KEY.data
        GOOGLE_APPLICATION_CREDENTIALS_PATH = form.GOOGLE_APPLICATION_CREDENTIALS_PATH.data
        BIG_QUERY_TARGET_ID = form.BIG_QUERY_TARGET_ID.data

        # get weather data based on input; main html with error message if no valid return
        url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATION}/{START_DATE}/{END_DATE}?unitGroup=metric&include=days&key={API_KEY}'
        response = requests.get(url)

        if response.status_code != 200:
            return render_template('main.html', form=form, error='Please check data entries')
        
        # upload valid entry inot BigQuery DB
        data = response.json()

        resDict = {
            "resolved_address": data['resolvedAddress'],
            "start_date": str(START_DATE),
            "end_date": str(END_DATE),
            "query_cost": str(data['queryCost']),
            "average_temp": str(round(np.array([d['temp'] for d in data['days']]).mean(), 1)),
            "max_cloudcover": str(round(np.array([d['cloudcover'] for d in data['days']]).max(), 1)),
            "fog": str(np.array([d['visibility'] < 1 for d in data['days']]).any()),
            "days_with_drizzle": str(np.array([any(set(x).intersection(set({'rain', 'freezingrain'}))) if x is not None else 0 for x in  [d['preciptype'] for d in data['days']]]).sum()),
            "runtime_timestamp": (datetime.utcnow() + timedelta(hours=data["tzoffset"])).strftime('%Y-%m-%d %H:%M:%S')
        }

        credentials =  service_account.Credentials.from_service_account_info(json.loads(GOOGLE_APPLICATION_CREDENTIALS_PATH.read()))
        client = bigquery.Client(credentials=credentials)

        client.insert_rows_json(
            BIG_QUERY_TARGET_ID, [resDict]
        )

        # get last 5 entries from BigQuery DB
        query = f"""
            SELECT *
            FROM `{BIG_QUERY_TARGET_ID.split(sep=".")[1] + '.' + BIG_QUERY_TARGET_ID.split(sep=".")[2]}`
            ORDER BY runtime_timestamp
            DESC LIMIT 5
        """
        job = client.query(query)

        # last entry and last 5 entries for front-end
        records = [dict(row) for row in job]
        data_json = json.dumps(resDict, indent = 4, separators = (',', ': '))

        return render_template(
            'post.html',
            form=form,
            json_data = data_json,
            records=records
        )

    return render_template('main.html', form=form)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))