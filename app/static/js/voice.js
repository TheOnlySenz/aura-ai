// Initialize SpeechRecognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;

// Initialize UI elements
const voiceButton = document.getElementById('voiceButton');
const listeningIndicator = document.getElementById('listeningIndicator');
const commandInput = document.getElementById('commandInput');

let isListening = false;

// Configure recognition
recognition.onstart = () => {
    isListening = true;
    voiceButton.classList.add('btn-danger');
    voiceButton.innerHTML = '<i class="fas fa-microphone-slash"></i> Stop Listening';
    listeningIndicator.classList.add('listening');
};

recognition.onend = () => {
    isListening = false;
    voiceButton.classList.remove('btn-danger');
    voiceButton.innerHTML = '<i class="fas fa-microphone"></i> Voice Input';
    listeningIndicator.classList.remove('listening');
};

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    commandInput.value = transcript;
    sendCommand(transcript);
};

recognition.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    if (event.error === 'no-speech') {
        showNotification('No speech detected');
    } else if (event.error === 'audio-capture') {
        showNotification('Microphone access denied');
    }
};

// Event listeners
voiceButton.addEventListener('click', () => {
    if (!isListening) {
        recognition.start();
    } else {
        recognition.stop();
    }
});

// Send command to server
function sendCommand(command) {
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
            addMessage(command, 'user');
            addMessage(data.result, 'assistant');
        } else {
            showNotification('Error: ' + data.message);
        }
    })
    .catch(error => {
        showNotification('Error: Failed to process command');
    });
}

// Add message to chat
function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    messageDiv.textContent = text;
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Show notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'alert alert-info alert-dismissible fade show';
    notification.innerHTML = `
        <strong>${message}</strong>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(notification, document.querySelector('.card'));
    setTimeout(() => notification.remove(), 3000);
}

// Request microphone permission
if (typeof window !== 'undefined') {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
            console.log('Microphone access granted');
        })
        .catch((err) => {
            console.error('Microphone access denied:', err);
            showNotification('Please grant microphone access to use voice commands');
        });
}
