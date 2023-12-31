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
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Unique Set
    event_key = db.Column(db.String(255))
    book_key =db.Column(db.String(255))
    market_key = db.Column(db.String(255))
    player = db.Column(db.String(255), nullable = True)
    
    name1 = db.Column(db.String(255))
    name2 = db.Column(db.String(255))
    
    price1 = db.Column(db.Float)
    price2 = db.Column(db.Float)
    
    point1 = db.Column(db.Float, nullable = True)
    point2 = db.Column(db.Float, nullable = True)
    
    
    def american_odds(self, num):
        price = None
        if num == 1:
            price = self.price1
        else:
            price = self.price2
            
        if price >= 2.00:
            return round((price - 1) * 100)
        elif 1.01 <= price < 2.00:
            return round(-100 / (price - 1))
        else:
            raise ValueError("Invalid decimal odds")
