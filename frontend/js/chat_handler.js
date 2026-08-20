/**
 * Common Chat Logic for Image, Audio, and Video pages
 */

class ChatHandler {
    constructor(mode) {
        this.mode = mode;
        this.sessionId = null;
        this.history = [];

        this.container = document.getElementById('chatContainer');
        this.historyEl = document.getElementById('chatHistory');
        this.inputEl = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('chatSendBtn');

        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.sendMessage());
            this.inputEl.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }
    }

    setSessionId(id) {
        this.sessionId = id;
        if (this.container) {
            this.container.style.opacity = '1';
            this.container.style.pointerEvents = 'auto';
        }
    }

    async sendMessage() {
        const question = this.inputEl.value.trim();
        if (!question || !this.sessionId || this.sendBtn.disabled) return;

        // 1. Add User Message
        this.addMessage('user', question);
        this.inputEl.value = '';

        // 2. Disable UI
        this.sendBtn.disabled = true;
        const typingId = this.addTypingIndicator();

        try {
            // 3. Call API
            const result = await API.chat(this.mode, this.sessionId, question);

            // 4. Remove Typing & Add AI Message
            this.removeTypingIndicator(typingId);
            if (result.status === 'success') {
                this.addMessage('ai', result.answer);
            } else {
                this.addMessage('ai', "Error: " + result.message);
            }
        } catch (error) {
            this.removeTypingIndicator(typingId);
            this.addMessage('ai', "Sorry, I'm having trouble connecting to the analysis server.");
            console.error(error);
        } finally {
            this.sendBtn.disabled = false;
        }
    }

    addMessage(role, text) {
        const msg = document.createElement('div');
        msg.className = `chat-message message-${role}`;
        msg.textContent = text;
        this.historyEl.appendChild(msg);
        this.historyEl.scrollTop = this.historyEl.scrollHeight;

        this.history.push({ role, text });
        if (this.history.length > 20) this.history.shift();
    }

    addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const indicator = document.createElement('div');
        indicator.id = id;
        indicator.className = 'typing-indicator';
        indicator.textContent = 'AI is thinking...';
        this.historyEl.appendChild(indicator);
        this.historyEl.scrollTop = this.historyEl.scrollHeight;
        return id;
    }

    removeTypingIndicator(id) {
        const indicator = document.getElementById(id);
        if (indicator) indicator.remove();
    }
}
