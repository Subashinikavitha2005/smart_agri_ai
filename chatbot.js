/* ════════════════════════════════
   chatbot.js — AI Chatbot + Voice
   ════════════════════════════════ */

let recognition = null;
let isListening = false;
let chatbotReady = false;

function initChatbot() {
    if (chatbotReady) return;
    chatbotReady = true;
    loadQuickTopics();
    initVoiceRecognition();
}

async function loadQuickTopics() {
    try {
        const data = await apiGet('/api/chatbot/topics');
        if (data.success) renderQuickTopics(data.topics);
    } catch {}
}

function renderQuickTopics(topics) {
    const container = document.getElementById('chatQuickTopics');
    container.innerHTML = topics.map(t => `
        <button class="quick-topic-btn" onclick="sendQuickTopic('${t.text.replace(/'/g,"\\'")}')">
            ${t.icon} ${currentLang === 'ta' ? t.text_ta : t.text}
        </button>
    `).join('');
}

function sendQuickTopic(text) {
    document.getElementById('chatInput').value = text;
    sendChatMessage();
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    appendChatMsg(message, 'user');

    // Typing indicator
    const typingId = appendTypingIndicator();

    try {
        const data = await apiPost('/api/chatbot/message', {
            message,
            language: currentLang
        });
        removeTypingIndicator(typingId);
        if (data.success) {
            appendChatMsg(data.response, 'bot');
        }
    } catch {
        removeTypingIndicator(typingId);
        appendChatMsg('Connection error. Please try again. / இணைப்பு பிழை.', 'bot');
    }
}

function appendChatMsg(text, role) {
    const container = document.getElementById('chatMessages');
    const avatar = role === 'bot' ? '🌾' : '👨‍🌾';
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.innerHTML = `
        <div class="chat-avatar">${avatar}</div>
        <div class="chat-bubble">${text}</div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const id = `typing-${Date.now()}`;
    const div = document.createElement('div');
    div.className = 'chat-msg bot';
    div.id = id;
    div.innerHTML = `
        <div class="chat-avatar">🌾</div>
        <div class="chat-bubble">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ─── Voice Recognition ───
function initVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        document.getElementById('voiceBtn').title = 'Voice not supported in this browser';
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = currentLang === 'ta' ? 'ta-IN' : 'en-IN';

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('chatInput').value = transcript;
        stopVoice();
        sendChatMessage();
    };

    recognition.onerror = () => {
        stopVoice();
        showToast('Voice recognition error. Please try again.', 'error');
    };

    recognition.onend = () => stopVoice();
}

function toggleVoice() {
    if (!recognition) {
        showToast('Voice not supported in this browser. / குரல் ஆதரவு இல்லை.', 'error');
        return;
    }
    if (isListening) {
        stopVoice();
    } else {
        startVoice();
    }
}

function startVoice() {
    recognition.lang = currentLang === 'ta' ? 'ta-IN' : 'en-IN';
    recognition.start();
    isListening = true;
    document.getElementById('voiceBtn').classList.add('listening');
    document.getElementById('voiceIndicator').classList.remove('hidden');
    showToast(currentLang === 'ta' ? '🎤 கேட்கிறேன்...' : '🎤 Listening...', 'info', 2000);
}

function stopVoice() {
    if (recognition) recognition.stop();
    isListening = false;
    document.getElementById('voiceBtn').classList.remove('listening');
    document.getElementById('voiceIndicator').classList.add('hidden');
}
