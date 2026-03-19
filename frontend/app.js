/* =========================================================
   MedicoAI – Chat Application Logic
   ========================================================= */

const API_URL = '/api/chat';

let conversationHistory = [];
let isSending = false;

// DOM references
const chatMessages = document.getElementById('chat-messages');
const chatInput    = document.getElementById('chat-input');
const sendBtn      = document.getElementById('send-btn');

/* ---------------------------------------------------------
   addMessage(text, sender)
   sender: "bot" | "user"
   --------------------------------------------------------- */
function addMessage(text, sender) {
  const messageEl = document.createElement('div');
  messageEl.classList.add('message', sender);

  if (sender === 'bot') {
    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.textContent = '🩺';
    messageEl.appendChild(avatar);
  }

  const bubbleGroup = document.createElement('div');
  bubbleGroup.classList.add('bubble-group');

  const bubble = document.createElement('div');
  bubble.classList.add('bubble');
  bubble.innerHTML = formatResponse(text);

  bubbleGroup.appendChild(bubble);
  messageEl.appendChild(bubbleGroup);

  chatMessages.appendChild(messageEl);
  scrollToBottom();

  return messageEl;
}

/* ---------------------------------------------------------
   showTyping()
   Returns the message element so the caller can remove it.
   --------------------------------------------------------- */
function showTyping() {
  const messageEl = document.createElement('div');
  messageEl.classList.add('message', 'bot');
  messageEl.id = 'typing-msg';

  const avatar = document.createElement('div');
  avatar.classList.add('avatar');
  avatar.textContent = '🩺';

  const bubbleGroup = document.createElement('div');
  bubbleGroup.classList.add('bubble-group');

  const indicator = document.createElement('div');
  indicator.classList.add('typing-indicator');
  indicator.innerHTML = '<span></span><span></span><span></span>';

  bubbleGroup.appendChild(indicator);
  messageEl.appendChild(avatar);
  messageEl.appendChild(bubbleGroup);

  chatMessages.appendChild(messageEl);
  scrollToBottom();

  return messageEl;
}

/* ---------------------------------------------------------
   formatResponse(text)
   Converts plain text with basic markdown into safe HTML.
   --------------------------------------------------------- */
function formatResponse(text) {
  if (!text) return '';

  // Escape HTML entities first to prevent XSS
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // **bold**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Bullet list lines: lines starting with "- " or "• "
  // Group consecutive bullet lines into a <ul>
  html = html.replace(/((?:^|\n)[•\-] .+)+/g, (match) => {
    const items = match
      .trim()
      .split('\n')
      .map(line => line.replace(/^[•\-]\s/, '').trim())
      .filter(Boolean)
      .map(item => `<li>${item}</li>`)
      .join('');
    return `<ul>${items}</ul>`;
  });

  // Newlines to <br> (but not inside block elements we just created)
  // We only replace \n that are NOT already consumed by the list block
  html = html.replace(/\n/g, '<br>');

  // Clean up <br> immediately before/after block elements
  html = html.replace(/<br>\s*(<\/?ul>|<\/?li>)/g, '$1');
  html = html.replace(/(<\/?ul>|<\/?li>)\s*<br>/g, '$1');

  return html;
}

/* ---------------------------------------------------------
   scrollToBottom()
   --------------------------------------------------------- */
function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ---------------------------------------------------------
   setInputEnabled(enabled)
   --------------------------------------------------------- */
function setInputEnabled(enabled) {
  chatInput.disabled = !enabled;
  sendBtn.disabled   = !enabled;
  isSending          = !enabled;
}

/* ---------------------------------------------------------
   sendMessage()
   --------------------------------------------------------- */
async function sendMessage() {
  if (isSending) return;

  const text = chatInput.value.trim();
  if (!text) return;

  // Hide suggestion chips after first user message
  const chips = document.getElementById('suggestion-chips');
  if (chips) chips.remove();

  chatInput.value = '';
  setInputEnabled(false);

  addMessage(text, 'user');
  conversationHistory.push({ role: 'user', content: text });

  const typingEl = showTyping();

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        conversation_history: conversationHistory.slice(-10),
      }),
    });

    typingEl.remove();

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const replyText = data.response || 'Sem resposta do servidor.';

    addMessage(replyText, 'bot');
    conversationHistory.push({ role: 'assistant', content: replyText });

  } catch (err) {
    typingEl.remove();
    console.error('[MedicoAI] Erro ao contatar API:', err);
    addMessage('Desculpe, ocorreu um erro. Tente novamente.', 'bot');
  } finally {
    setInputEnabled(true);
    chatInput.focus();
  }
}

/* ---------------------------------------------------------
   Suggestion chip handler
   --------------------------------------------------------- */
function handleChipClick(e) {
  const chip = e.target.closest('.chip');
  if (!chip) return;
  const text = chip.dataset.text;
  if (text) {
    chatInput.value = text;
    sendMessage();
  }
}

/* ---------------------------------------------------------
   Event listeners
   --------------------------------------------------------- */
sendBtn.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Chips delegated listener (chips may be removed later, delegation from parent is safe)
chatMessages.addEventListener('click', handleChipClick);

// Focus input on load
window.addEventListener('DOMContentLoaded', () => {
  chatInput.focus();
});
