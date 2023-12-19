# app/models.py
from app import db


class Bookie(db.Model):
    book_key = db.Column(db.String(255), primary_key=True)
    book_name = db.Column(db.String(255), unique=True, nullable=False)
    bk_last_update = db.Column(db.String(255), nullable=False)

class Market(db.Model):
    market_key = db.Column(db.String(255), primary_key=True)
    mk_last_update = db.Column(db.String(255))

class Player(db.Model):
    key = db.Column(db.String(255), primary_key=True)

class Team(db.Model):
    key = db.Column(db.String(255), primary_key=True)

class Event(db.Model):
    key = db.Column(db.String(255), primary_key=True)
    sport_key = db.Column(db.String(255))
    commence_time = db.Column(db.String(255))
    home_team = db.Column(db.String(255))
    away_team = db.Column(db.String(255))

class Odds(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    event_key = db.Column(db.String(255))
    book_key =db.Column(db.String(255))
    market_key = db.Column(db.String(255))
    
    name = db.Column(db.String(255))
    price = db.Column(db.Float)
    point = db.Column(db.Float, nullable = True)