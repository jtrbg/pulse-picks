from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Import the Config class from config.py

app = Flask(__name__)
app.config.from_object(Config)  # Use the configuration from Config class

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Adjust the database URI as needed

db = SQLAlchemy(app)

from app import routes, models
