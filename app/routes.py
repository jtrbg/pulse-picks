# app/routes.py
from flask import jsonify, request, render_template, current_app
from app import app, db
from app.models import Bookie, Market, Event, Odds
from app.models import Player, Team
import requests
from datetime import datetime
import pytz

API_KEY = current_app.config['API_KEY']
ODDS_API_BASE_URL = 'https://api.the-odds-api.com/v4/sports'
# Markets for player props
mk_plyr = [
    'player_pass_tds',
    'player_pass_yds',
    'player_pass_completions',
    'player_pass_attempts',
    'player_pass_interceptions',
    'player_pass_longest_completion',
    'player_rush_yds',
    'player_rush_attempts',
    'player_rush_longest',
    'player_receptions',
    'player_reception_yds',
    'player_reception_longest',
    'player_kicking_points',
    'player_field_goals',
    'player_tackles_assists',
    'player_1st_td',
    'player_last_td',
    'player_anytime_td']

@app.route('/')
def index():
    events = Event.query.all()

    formatted_events = []
    for event in events:
        # Parse the commence_time string and convert to UTC
        commence_time_utc = datetime.strptime(event.commence_time, "%Y-%m-%dT%H:%M:%SZ")
        commence_time_utc = commence_time_utc.replace(tzinfo=pytz.UTC)

        # Convert to local timezone (replace 'America/New_York' with your local timezone)
        local_timezone = pytz.timezone('America/New_York')
        commence_time_local = commence_time_utc.astimezone(local_timezone)

        # Format the local time
        formatted_date_time = commence_time_local.strftime("%A - %B %d %Y - %H:%M")

        # Add the formatted date to the event object
        event.formatted_date_time = formatted_date_time

        formatted_events.append(event)

    return render_template('index.html', events=formatted_events)
def update_nfl_market(market):
    api_key = API_KEY
    sport = 'americanfootball_nfl'
    regions = 'us'
    
    url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={api_key}&regions={regions}&markets={market}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # data needs to be a list
        if isinstance(data, list):
            # Process each event in the API response
            for event in data:
                key = event['id']
                sport_key = event['sport_key']
                commence_time = event['commence_time']
                home_team = event['home_team']
                away_team = event['away_team']
                print(f'{key} {sport_key}, {commence_time} {home_team} {away_team}')
                # Checks for existing event key(unique)
                eventO = Event.query.filter_by(key=key).first()
                if not eventO:
                    eventO = Event(key=key,sport_key=sport_key,commence_time=commence_time,home_team=home_team, away_team= away_team)
                    db.session.add(eventO)
                # Process each bookie that have odds for the event
                for book in event['bookmakers']:
                    book_key = book.get('key',[])
                    book_name = book.get('title',[])
                    bk_last_update = book.get('last_update',[])
                    
                    # Checks for existing bookie key(unique)
                    bookmaker = Bookie.query.filter_by(book_key=book_key).first()
                    if not bookmaker:
                        bookmaker = Bookie(book_key=book_key,book_name=book_name,bk_last_update=bk_last_update)
                        db.session.add(bookmaker)
                        
                    # Process each market that a bookie has
                    for market in book.get('markets'):
                        market_key = market.get('key',[])
                        mk_last_update = market.get('last_update',[])
                        
                        # Checks for existing market key(unique)
                        market_current = Market.query.filter_by(market_key=market_key).first()
                        if not market_current:
                            market_current = Market(market_key=market_key,mk_last_update=mk_last_update)
                            db.session.add(market_current)
                        
                        # Process each outcome/odds for a market
                        for outcome in market.get('outcomes'):
                            name = outcome.get('name',[])
                            price = outcome.get('price',[])
                            point = None
                            if any('point' in key for key in outcome):
                                point = outcome.get('point',[])

                            #Checks for existing Odds row with same values (plural unique)
                            odds_current = Odds.query.filter_by(event_key = key, book_key=book_key, market_key=market_key,name=name, price=price, point=point).first()
                            if not odds_current:
                                odds_current = Odds(event_key = key, book_key=book_key, market_key=market_key,name=name, price=price, point=point)
                                db.session.add(odds_current)

        # Handle other cases as needed
        else:
            return 'Unexpected response format'

        # Commit changes to the database
        db.session.commit()

        return 'Bets added to the database successfully'
    else:
        return f'Failed to fetch odds data. Status Code: {response.status_code}'

# Route to update the bets in the database from the Odds API
# API cost: 3 requests
@app.route('/api/update_nfl_game_odds_db') 
def update_nfl_game_odds():
    api_key = API_KEY
    sport = 'americanfootball_nfl'
    regions = 'us'
    
    # Markets for game lines
    mk_game = ['h2h','spreads','totals']

    output = ''
    # For each market, makes an API call
    for market in mk_game:
        response = update_nfl_market(market)
        mk_response = f'{market} : {response}'
        output = f'{output}\n{mk_response}'
        
    return jsonify({'message': output})


# Route to display all bets in the database
@app.route('/api/all_bets')
def get_all_bets():
    bets = Bet.query.all()

    bets_data = [{'id': bet.id, 'amount': bet.amount, 'odds_id': bet.odds_id} for bet in bets]

    return jsonify({'bets_data': bets_data})

# Route to view all data in the database
@app.route('/api/view_database')
def view_database():
    # Retrieve all data from the database
    bookies = Bookie.query.all()
    markets = Market.query.all()
    players = Player.query.all()
    teams = Team.query.all()
    events = Event.query.all()
    odds = Odds.query.all()

    # Convert data to a dictionary for JSON serialization
    data = {
        'bookies': [{'book_key': b.book_key, 'book_name': b.book_name, 'bk_last_update': b.bk_last_update} for b in bookies],
        'markets': [{'market_key': m.market_key, 'mk_last_update': m.mk_last_update} for m in markets],
        'players': [{'key': p.key} for p in players],
        'teams': [{'key': t.key} for t in teams],
        'events': [{'key': e.key, 'sport_key': e.sport_key, 'commence_time': e.commence_time, 'home_team': e.home_team, 'away_team': e.away_team} for e in events],
        'odds': [
            {'id': o.id, 'event_key': o.event_key, 'book_key': o.book_key, 'market_key': o.market_key, 'name': o.name, 'price': o.price, 'point': o.point}
            for o in odds
        ],
    }

    return jsonify(data)

# Route to fetch odds for a specific sport with provided parameters
@app.route('/api/sports/<sport>/odds')
def get_sport_odds(sport):
    api_key = request.args.get('apiKey')
    regions = request.args.get('regions')
    markets = request.args.get('markets')

    if api_key != API_KEY:
        return jsonify({'error': 'Invalid API key'}), 401

    url = f'{ODDS_API_BASE_URL}/{sport}/odds/?apiKey={api_key}&regions={regions}&markets={markets}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({'error': f'Failed to fetch odds. Status Code: {response.status_code}'}), 500
