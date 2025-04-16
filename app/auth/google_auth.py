from flask import Blueprint, redirect, url_for, session, request
from flask_oauthlib.client import OAuth
from authlib.integrations.flask_client import OAuth as AuthLibOAuth
from app.models.user import User
from app import db
import os

auth_bp = Blueprint('google_auth', __name__)
oauth = OAuth()

def configure_google_auth(app):
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
        redirect_uri=os.getenv('GOOGLE_REDIRECT_URI')
    )
    return google

@auth_bp.route('/login')
def login():
    google = configure_google_auth(current_app)
    redirect_uri = url_for('google_auth.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize')
def authorize():
    google = configure_google_auth(current_app)
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    
    # Get user info
    email = user_info['email']
    name = user_info['name']
    picture = user_info.get('picture')
    
    # Create or update user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            username=name,
            email=email,
            # Password is not needed since we use Google OAuth
            password_hash='',
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        
        # Create default preferences
        preferences = UserPreferences(
            user=user,
            language='en',
            timezone='UTC'
        )
        db.session.add(preferences)
        db.session.commit()
    
    # Login user
    login_user(user)
    user.update_last_login()
    db.session.commit()
    
    return redirect(url_for('main.index'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index'))
