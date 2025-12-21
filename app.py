from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import requests
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# API configuration - points to FastAPI backend
API_BASE = os.getenv('API_BASE', 'http://localhost:8000')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'change-me-in-production')

# Admin password for login
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

def get_headers():
    """Get headers for API requests"""
    return {
        'Authorization': f'Bearer {ADMIN_TOKEN}',
        'Content-Type': 'application/json'
    }

def api_request(method, endpoint, data=None, params=None):
    """Make API request with error handling"""
    try:
        url = f'{API_BASE}{endpoint}'
        if method == 'GET':
            response = requests.get(url, headers=get_headers(), params=params)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=get_headers(), params=params)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=get_headers(), params=params)
        elif method == 'DELETE':
            response = requests.delete(url, headers=get_headers(), params=params)
        else:
            raise ValueError(f'Unsupported method: {method}')
        
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.exceptions.RequestException as e:
        flash(f'API Error: {str(e)}', 'error')
        return None

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ===== AUTHENTICATION =====

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            next_url = request.args.get('next', url_for('index'))
            flash('Login successful', 'success')
            return redirect(next_url)
        else:
            flash('Invalid password', 'error')
    
    # If already logged in, redirect to dashboard
    if session.get('logged_in'):
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Dashboard"""
    return render_template('index.html', API_BASE=API_BASE, ADMIN_TOKEN=ADMIN_TOKEN)

# ===== MESSAGES MANAGEMENT =====

@app.route('/messages')
@login_required
def list_messages():
    """List all messages"""
    messages = api_request('GET', '/api/messages')
    if messages is None:
        messages = []
    return render_template('messages.html', messages=messages)

@app.route('/messages/new', methods=['GET', 'POST'])
@login_required
def new_message():
    """Create a new message"""
    if request.method == 'POST':
        message_data = request.get_json()
        result = api_request('POST', '/api/messages', message_data)
        if result:
            flash('Message created successfully', 'success')
            return jsonify(result)
        return jsonify({'error': 'Failed to create message'}), 400
    
    return render_template('message_form.html', message=None)

@app.route('/messages/<message_id>')
@login_required
def view_message(message_id):
    """View a single message"""
    message = api_request('GET', f'/api/messages/{message_id}')
    if message is None:
        flash('Message not found', 'error')
        return redirect(url_for('list_messages'))
    return render_template('message_view.html', message=message)

@app.route('/messages/<message_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_message(message_id):
    """Edit a message"""
    if request.method == 'POST':
        updates = request.get_json()
        result = api_request('PUT', f'/api/messages/{message_id}', updates)
        if result:
            flash('Message updated successfully', 'success')
            return jsonify(result)
        return jsonify({'error': 'Failed to update message'}), 400
    
    # GET - load message
    message = api_request('GET', f'/api/messages/{message_id}')
    if message is None:
        flash('Message not found', 'error')
        return redirect(url_for('list_messages'))
    return render_template('message_form.html', message=message)

@app.route('/messages/<message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """Delete a message"""
    result = api_request('DELETE', f'/api/messages/{message_id}')
    if result:
        flash('Message deleted successfully', 'success')
    return redirect(url_for('list_messages'))

# ===== CANDIDATES MANAGEMENT =====

@app.route('/candidates')
@login_required
def list_candidates():
    """List all recruitment candidates"""
    candidates = api_request('GET', '/api/admin/recruitment/candidates')
    if candidates is None:
        candidates = []
    return render_template('candidates.html', candidates=candidates)

@app.route('/candidates/new', methods=['GET', 'POST'])
@login_required
def new_candidate():
    """Create a new candidate"""
    if request.method == 'POST':
        candidate_data = request.get_json()
        result = api_request('POST', '/api/admin/recruitment/candidates', candidate_data)
        if result:
            flash('Candidate created successfully', 'success')
            return jsonify(result)
        return jsonify({'error': 'Failed to create candidate'}), 400
    
    return render_template('candidate_form.html', candidate=None)

@app.route('/candidates/<candidate_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_candidate(candidate_id):
    """Edit a candidate"""
    if request.method == 'POST':
        updates = request.get_json()
        result = api_request('PUT', f'/api/admin/recruitment/candidates/{candidate_id}', updates)
        if result:
            flash('Candidate updated successfully', 'success')
            return jsonify(result)
        return jsonify({'error': 'Failed to update candidate'}), 400
    
    # GET - load candidate
    candidates = api_request('GET', '/api/admin/recruitment/candidates')
    if candidates is None:
        candidates = []
    candidate = next((c for c in candidates if c.get('id') == candidate_id), None)
    if not candidate:
        flash('Candidate not found', 'error')
        return redirect(url_for('list_candidates'))
    return render_template('candidate_form.html', candidate=candidate)

@app.route('/candidates/<candidate_id>/delete', methods=['POST'])
@login_required
def delete_candidate(candidate_id):
    """Delete a candidate"""
    result = api_request('DELETE', f'/api/admin/recruitment/candidates/{candidate_id}')
    if result:
        flash('Candidate deleted successfully', 'success')
    return redirect(url_for('list_candidates'))

# ===== GAMES MANAGEMENT =====

@app.route('/games/in-progress')
@login_required
def list_games_in_progress():
    """List all games in progress with pagination"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    offset = (page - 1) * limit
    
    params = {'limit': limit, 'offset': offset}
    result = api_request('GET', '/api/games/in-progress', params=params)
    
    if result is None:
        games = []
        total = 0
        has_more = False
    else:
        games = result.get('games', [])
        total = result.get('total', 0)
        has_more = result.get('has_more', False)
    
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    
    return render_template('games_in_progress.html', 
                         games=games, 
                         page=page, 
                         total_pages=total_pages,
                         total=total,
                         has_more=has_more,
                         limit=limit)

@app.route('/games/historical')
@login_required
def list_historical_games():
    """List all historical games with pagination"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    offset = (page - 1) * limit
    
    params = {'limit': limit, 'offset': offset}
    result = api_request('GET', '/api/games/historical', params=params)
    
    if result is None:
        games = []
        total = 0
        has_more = False
    else:
        games = result.get('games', [])
        total = result.get('total', 0)
        has_more = result.get('has_more', False)
    
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    
    return render_template('games_historical.html', 
                         games=games, 
                         page=page, 
                         total_pages=total_pages,
                         total=total,
                         has_more=has_more,
                         limit=limit)

@app.route('/games/map')
@login_required
def games_map():
    """Map view of all games (current and historical)"""
    # Get all games without pagination for map
    # We'll fetch a large number to get all games
    params_in_progress = {'limit': 10000, 'offset': 0}
    params_historical = {'limit': 10000, 'offset': 0}
    
    result_in_progress = api_request('GET', '/api/games/in-progress', params=params_in_progress)
    result_historical = api_request('GET', '/api/games/historical', params=params_historical)
    
    games_in_progress = result_in_progress.get('games', []) if result_in_progress else []
    games_historical = result_historical.get('games', []) if result_historical else []
    
    # Parse geolocation and prepare markers
    markers = []
    
    # Process in-progress games
    for game in games_in_progress:
        geo = game.get('geolocation')
        if geo:
            try:
                # Parse "lat,lng" format
                parts = geo.split(',')
                if len(parts) == 2:
                    lat = float(parts[0].strip())
                    lng = float(parts[1].strip())
                    markers.append({
                        'lat': lat,
                        'lng': lng,
                        'type': 'in_progress',
                        'fund_name': game.get('fund_name', 'Unknown'),
                        'time_started': game.get('time_started', ''),
                        'id': game.get('id', '')
                    })
            except (ValueError, AttributeError):
                # Skip invalid geolocation
                continue
    
    # Process historical games
    for game in games_historical:
        geo = game.get('geolocation')
        if geo:
            try:
                # Parse "lat,lng" format
                parts = geo.split(',')
                if len(parts) == 2:
                    lat = float(parts[0].strip())
                    lng = float(parts[1].strip())
                    markers.append({
                        'lat': lat,
                        'lng': lng,
                        'type': 'historical',
                        'fund_name': game.get('fund_name', 'Unknown'),
                        'time_started': game.get('time_started', ''),
                        'time_ended': game.get('time_ended', ''),
                        'total_pnl': game.get('total_pnl'),
                        'id': game.get('id', '')
                    })
            except (ValueError, AttributeError):
                # Skip invalid geolocation
                continue
    
    return render_template('games_map.html', markers=markers)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, port=port, host='0.0.0.0')

