from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, UserPreferences
from app import db
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.update_last_login()
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Logged in successfully',
                'user': user.to_dict()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validate input
        if not username or not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'All fields are required'
            }), 400
            
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email format'
            }), 400
            
        if len(password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'Password must be at least 8 characters long'
            }), 400
            
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                'status': 'error',
                'message': 'Email already registered'
            }), 400
            
        if User.query.filter_by(username=username).first():
            return jsonify({
                'status': 'error',
                'message': 'Username already taken'
            }), 400
            
        # Create new user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        # Create default preferences
        preferences = UserPreferences(
            user=user
        )
        
        db.session.add(user)
        db.session.add(preferences)
        db.session.commit()
        
        login_user(user)
        return jsonify({
            'status': 'success',
            'message': 'Registration successful',
            'user': user.to_dict()
        })
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    })

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@auth.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def api_profile():
    if request.method == 'PUT':
        data = request.get_json()
        
        # Update user info
        current_user.username = data.get('username', current_user.username)
        current_user.email = data.get('email', current_user.email)
        
        # Update preferences
        if current_user.preferences:
            current_user.preferences.language = data.get('language', current_user.preferences.language)
            current_user.preferences.timezone = data.get('timezone', current_user.preferences.timezone)
            current_user.preferences.voice_id = data.get('voice_id', current_user.preferences.voice_id)
            current_user.preferences.speaking_rate = data.get('speaking_rate', current_user.preferences.speaking_rate)
            current_user.preferences.volume = data.get('volume', current_user.preferences.volume)
            current_user.preferences.theme = data.get('theme', current_user.preferences.theme)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': current_user.to_dict(),
            'preferences': current_user.preferences.to_dict()
        })
    
    return jsonify({
        'status': 'success',
        'user': current_user.to_dict(),
        'preferences': current_user.preferences.to_dict()
    })

@auth.route('/api/preferences', methods=['GET', 'PUT'])
@login_required
def preferences():
    if request.method == 'PUT':
        data = request.get_json()
        
        if current_user.preferences:
            current_user.preferences.language = data.get('language', current_user.preferences.language)
            current_user.preferences.timezone = data.get('timezone', current_user.preferences.timezone)
            current_user.preferences.voice_id = data.get('voice_id', current_user.preferences.voice_id)
            current_user.preferences.speaking_rate = data.get('speaking_rate', current_user.preferences.speaking_rate)
            current_user.preferences.volume = data.get('volume', current_user.preferences.volume)
            current_user.preferences.theme = data.get('theme', current_user.preferences.theme)
            db.session.commit()
            
        return jsonify({
            'status': 'success',
            'message': 'Preferences updated successfully',
            'preferences': current_user.preferences.to_dict()
        })
    
    return jsonify({
        'status': 'success',
        'preferences': current_user.preferences.to_dict()
    })

@auth.route('/api/command_history')
@login_required
def command_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    history = CommandHistory.query.filter_by(user_id=current_user.id)
    
    if request.args.get('search'):
        search_term = request.args.get('search')
        history = history.filter(
            CommandHistory.command.ilike(f'%{search_term}%') |
            CommandHistory.response.ilike(f'%{search_term}%')
        )
    
    history = history.order_by(CommandHistory.created_at.desc())
    paginated_history = history.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'status': 'success',
        'history': [item.to_dict() for item in paginated_history.items],
        'total': paginated_history.total,
        'pages': paginated_history.pages,
        'current_page': page
    })
