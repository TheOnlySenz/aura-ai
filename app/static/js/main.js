// Initialize variables
let currentLanguage = 'en';
let currentVoice = null;
let speakingRate = 200;
let volume = 100;

// Initialize speech recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;

// Initialize UI elements
const commandInput = document.getElementById('commandInput');
const sendCommand = document.getElementById('sendCommand');
const voiceButton = document.getElementById('voiceButton');
const settingsButton = document.getElementById('settingsButton');
const chatHistory = document.getElementById('chatHistory');
const languageSelect = document.getElementById('languageSelect');
const voiceSelect = document.getElementById('voiceSelect');
const speakingRateRange = document.getElementById('speakingRate');
const volumeRange = document.getElementById('volume');
const rateValue = document.querySelector('.rate-value');
const volumeValue = document.querySelector('.volume-value');
const settingsModal = new bootstrap.Modal(document.getElementById('settingsModal'));
const saveSettings = document.getElementById('saveSettings');

// Event listeners
sendCommand.addEventListener('click', sendCommandHandler);
voiceButton.addEventListener('click', toggleVoiceRecognition);
settingsButton.addEventListener('click', loadSettings);
saveSettings.addEventListener('click', saveSettingsHandler);

// Speech recognition handlers
recognition.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    commandInput.value = transcript;
    sendCommandHandler();
};

recognition.onerror = function(event) {
    console.error('Speech recognition error:', event.error);
};

// Command sending handler
function sendCommandHandler() {
    const command = commandInput.value.trim();
    if (!command) return;

    // Add user message to chat
    addMessage(command, 'user');
    
    // Send command to server
    fetch('/api/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            addMessage(data.result, 'assistant');
        } else {
            addMessage('Error: ' + data.message, 'assistant');
        }
    })
    .catch(error => {
        addMessage('Error: Failed to process command', 'assistant');
    });

    commandInput.value = '';
}

// Toggle voice recognition
function toggleVoiceRecognition() {
    if (recognition.start) {
        recognition.start();
        voiceButton.innerHTML = '<i class="fas fa-microphone-slash"></i> Stop Listening';
        voiceButton.classList.add('btn-danger');
    } else {
        recognition.stop();
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i> Voice Input';
        voiceButton.classList.remove('btn-danger');
    }
}

// Add message to chat
function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    messageDiv.textContent = text;
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Load settings
function loadSettings() {
    fetch('/api/preferences')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentLanguage = data.preferences.language;
                speakingRate = data.preferences.speaking_rate;
                volume = data.preferences.volume;
                
                // Update UI
                loadLanguageOptions();
                loadVoiceOptions();
                speakingRateRange.value = speakingRate;
                volumeRange.value = volume;
                rateValue.textContent = speakingRate;
                volumeValue.textContent = volume;
                
                settingsModal.show();
            }
        });
}

// Save settings
function saveSettingsHandler() {
    const settings = {
        language: languageSelect.value,
        voice_id: voiceSelect.value,
        speaking_rate: speakingRateRange.value,
        volume: volumeRange.value
    };

    fetch('/api/preferences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            settingsModal.hide();
            showNotification('Settings saved successfully');
        } else {
            showNotification('Error saving settings');
        }
    });
}

// Load language options
function loadLanguageOptions() {
    const languages = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'hi': 'Hindi',
        'ar': 'Arabic'
    };

    languageSelect.innerHTML = '';
    Object.entries(languages).forEach(([code, name]) => {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = name;
        if (code === currentLanguage) option.selected = true;
        languageSelect.appendChild(option);
    });
}

// Load voice options
function loadVoiceOptions() {
    fetch('/api/voices')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                voiceSelect.innerHTML = '';
                data.voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.id;
                    option.textContent = voice.name;
                    if (voice.id === currentVoice) option.selected = true;
                    voiceSelect.appendChild(option);
                });
            }
        });
}

// Update rate and volume values
speakingRateRange.addEventListener('input', () => {
    rateValue.textContent = speakingRateRange.value;
});

volumeRange.addEventListener('input', () => {
    volumeValue.textContent = volumeRange.value;
});

// Show notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'alert alert-success alert-dismissible fade show';
    notification.innerHTML = `
        <strong>${message}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(notification, document.querySelector('.card'));
    setTimeout(() => notification.remove(), 3000);
}

// Request microphone permission on page load
window.addEventListener('load', () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
            console.log('Microphone access granted');
        })
        .catch((err) => {
            console.error('Microphone access denied:', err);
            showNotification('Please grant microphone access to use voice commands');
        });
});
