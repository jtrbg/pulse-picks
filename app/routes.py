# app/routes.py
from flask import jsonify, request, render_template, current_app
from app import app, db
from app.models import Bookie, Market, Event, Odds
from app.models import Player, Team
import requests
from datetime import datetime
import pytz

ODDS_API_BASE_URL = 'https://api.the-odds-api.com/v4/sports'
# Markets for player props


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

# only two way 
def update_plyr_market(market, eventID):
    with app.app_context():
        api_key = current_app.config['API_KEY']
    sport = 'americanfootball_nfl'
    regions = 'us'
    
    url = f'https://api.the-odds-api.com/v4/sports/{sport}/events/{eventID}/odds?apiKey={api_key}&regions={regions}&markets={market}'
    response = requests.get(url)

    if response.status_code == 200:
        event = response.json()
        key = event.get('id',[])
        
        # Process each book that has an market for that event
        for book in event['bookmakers']:
            book_key = book.get('key', [])
            # Process each outcome in a bookie's market
            outcome1 = book.get('markets', [])[0].get('outcomes', [])[0]
            
            
            player = outcome1.get('description', None) # Combine on player
            
            name1 = outcome1.get('name', [])
            name2 = None
            
            price1 = outcome1.get('price', [])
            name2 = None
            
            point1 = outcome1.get('point', None)
            point2 =None
            
            if(len(book.get('markets', [])[0].get('outcomes', [])) > 1):
                outcome2 = book.get('markets', [])[0].get('outcomes', [])[1]
                name2 = outcome2.get('name', [])
                price2 = outcome2.get('price', [])
                point2 = outcome2.get('point', None)
            # If there is no Odds object with that set of data
            odds_current = Odds.query.filter_by(event_key=key, book_key=book_key, market_key=market, name1=name1,name2=name2, price1=price1,price2=price2, point1=point1, point2=point2, player=player).first()
            if not odds_current:
                odds_current = Odds(event_key=key, book_key=book_key, market_key=market, name1=name1,name2=name2, price1=price1,price2=price2, point1=point1, point2=point2, player=player)
                db.session.add(odds_current) # add it
        db.session.commit() # Commit each event
    else:
        return f'Failed to fetch odds data. Status Code: {response.status_code}'

@app.route('/sorted_odds/<event_key>')
def sorted_odds(event_key):
    # Markets for player props
    mk_game = ['h2h','spreads','totals']
    mk_plyr = [
        'player_pass_tds', 'player_pass_yds', 'player_pass_completions', 'player_pass_attempts',
        'player_pass_interceptions', 'player_pass_longest_completion', 'player_rush_yds', 'player_rush_attempts',
        'player_rush_longest', 'player_receptions', 'player_reception_yds', 'player_reception_longest',
        'player_kicking_points', 'player_field_goals', 'player_tackles_assists', 'player_1st_td', 'player_last_td',
        'player_anytime_td'
    ]
    
    mkg_new = {'h2h': 'Moneyline', 'spreads': 'Spread', 'totals': 'Total'}
    mkp_new = {
        'player_pass_tds': 'Passing TDs',
        'player_pass_yds': 'Passing Yds',
        'player_pass_completions': 'Completions',
        'player_pass_attempts': 'Pass Attempts',
        'player_pass_interceptions': 'Interceptions',
        'player_pass_longest_completion': 'Longest Completion',
        'player_rush_yds': 'Rushing Yds',
        'player_rush_attempts': 'Rush Attempts',
        'player_rush_longest': 'Longest Rush',
        'player_receptions': 'Receptions',
        'player_reception_yds': 'Rec. Yds',
        'player_reception_longest': 'Longest Reception',
        'player_kicking_points': 'Kicking Points',
        'player_field_goals': 'Field Goals',
        'player_tackles_assists': 'Tackles + Assist',
        'player_1st_td': 'First TD',
        'player_last_td': 'Last TD',
        'player_anytime_td': 'Anytime TD'
    }

    # Updates the market, down for now to test with lines
    output = ''
    # For each market, make an API call only once per day per event
    for market in mk_plyr:
        response = update_plyr_market(market, event_key)
        mk_response = f'{market} : {response}'
        output = f'{output}\n{mk_response}\n'
        print(output)
    # Query the database to get sorted odds for the specific event
    
    mk_game_queries = {mkg: Odds.query.filter_by(event_key=event_key, market_key=mkg).order_by(Odds.market_key, Odds.book_key).all() for mkg in mk_game}
    mk_plyr_queries = {mkp: Odds.query.filter_by(event_key=event_key, market_key=mkp).order_by(Odds.market_key, Odds.book_key).all() for mkp in mk_plyr}
    
    # Render the template with the sorted odds
    return render_template('sorted_odds.html', sorted_odds=mk_game_queries, sorted_props=mk_plyr_queries, mkg_new=mkg_new,mkp_new=mkp_new)

#------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------
# Only 2 way
def update_nfl_market(market):
    with app.app_context():
        api_key = current_app.config['API_KEY']
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
                        # print(book.get('markets', [])[0].get('outcomes', []))
                        # print(book.get('markets', [])[0].get('outcomes', [])[0])
                        # print(book.get('markets', [])[0].get('outcomes', [])[1])
                        outcome1 = book.get('markets', [])[0].get('outcomes', [])[0]
                        outcome2 = book.get('markets', [])[0].get('outcomes', [])[1]
                        
                        name1 = outcome1.get('name', [])
                        name2 = outcome2.get('name', [])
            
                        price1 = outcome1.get('price', [])
                        price2 = outcome2.get('price', [])

                        point1 = None
                        point2 = None
                        if any('point' in key for key in outcome1):
                            point1 = outcome1.get('point',[])
                        if any('point' in key for key in outcome2):
                            point2 = outcome2.get('point',[])

                        #Checks for existing Odds row with same values (plural unique)
                        odds_current = Odds.query.filter_by(event_key=key, book_key=book_key, market_key=market_key, name1=name1,name2=name2, price1=price1,price2=price2, point1=point1, point2=point2).first()
                        if not odds_current:
                            odds_current = Odds(event_key=key, book_key=book_key, market_key=market_key, name1=name1,name2=name2, price1=price1,price2=price2, point1=point1, point2=point2)
                            db.session.add(odds_current) # add it

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
@app.route('/api/update_nfl_game_odds') 
def update_nfl_game_odds():
    # Markets for game lines
    mk_game = ['h2h','spreads','totals']

    output = ''
    # For each market, makes an API call
    for market in mk_game:
        response = update_nfl_market(market)
        mk_response = f'{market} : {response}'
        output = f'{output}\n{mk_response}'
        
    return jsonify({'message': output})

#------------------------------------------------------------------------------------------------------

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
            {'id': o.id, 'event_key': o.event_key, 'book_key': o.book_key, 'market_key': o.market_key, 'name1': o.name1,'name2': o.name2, 'price1': o.price1,'price2': o.price2, 'point1': o.point1,'point2': o.point2, 'player': o.player}
            for o in odds
        ],
    }

    return jsonify(data)