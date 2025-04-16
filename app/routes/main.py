from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.user import UserPreferences
from app.services.email_service import get_email_service
from app.aura_ai import AuraAI
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/api/command', methods=['POST'])
@login_required
def process_command():
    data = request.get_json()
    command = data.get('command', '')
    
    # Initialize AuraAI with user preferences
    aura = AuraAI()
    preferences = UserPreferences.query.filter_by(user_id=current_user.id).first()
    
    if preferences:
        aura.set_language(preferences.language)
        aura.set_voice(preferences.voice_id)
        aura.set_rate(preferences.speaking_rate)
        aura.set_volume(preferences.volume)
    
    # Process the command
    result = aura.process_command(command)
    
    # Handle email commands
    if command.startswith('email'):
        parts = command.split()
        if len(parts) >= 4:  # email [recipient] [subject] [body]
            recipient = parts[1]
            subject = parts[2]
            body = ' '.join(parts[3:])
            
            email_service = get_email_service()
            result = email_service.send_email(
                to_email=recipient,
                subject=subject,
                body=body
            )
    
    return jsonify({
        'status': 'success',
        'result': result
    })

@main_bp.route('/api/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    preferences = UserPreferences.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        data = request.get_json()
        preferences.language = data.get('language', preferences.language)
        preferences.timezone = data.get('timezone', preferences.timezone)
        preferences.voice_id = data.get('voice_id', preferences.voice_id)
        preferences.speaking_rate = data.get('speaking_rate', preferences.speaking_rate)
        preferences.volume = data.get('volume', preferences.volume)
        
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Preferences updated successfully'
        })
    
    return jsonify({
        'status': 'success',
        'preferences': {
            'language': preferences.language,
            'timezone': preferences.timezone,
            'voice_id': preferences.voice_id,
            'speaking_rate': preferences.speaking_rate,
            'volume': preferences.volume
        }
    })

@main_bp.route('/api/voices', methods=['GET'])
@login_required
def get_voices():
    aura = AuraAI()
    return jsonify({
        'status': 'success',
        'voices': aura.list_voices()
    })
