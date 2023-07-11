from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import InputRequired
from flask_wtf.file import FileField, FileRequired

from datetime import date

class SearchForm(FlaskForm):
    LOCATION = StringField('City', validators=[InputRequired()], description='Enter City')
    START_DATE = DateField('From date', default=date.today(), validators=[InputRequired()],)
    END_DATE = DateField('To date', default=date.today(), validators=[InputRequired()])
    API_KEY = StringField('API Key', validators=[InputRequired()], description='Provide valid API key')
    GOOGLE_APPLICATION_CREDENTIALS_PATH = FileField('Google Application Credentials Path', validators=[FileRequired()])
    BIG_QUERY_TARGET_ID = StringField('BigQuery Target ID', validators=[InputRequired()], description='Provide BigQuery Target ID')