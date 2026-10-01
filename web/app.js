document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const connectionStatus = document.getElementById('connectionStatus');
  const statusText = connectionStatus.querySelector('.status-text');
  const logTerminal = document.getElementById('logTerminal');
  const clearLogsBtn = document.getElementById('clearLogsBtn');
  const micBtn = document.getElementById('micBtn');
  const micStatus = document.getElementById('micStatus');
  const textForm = document.getElementById('textForm');
  const textInput = document.getElementById('textInput');

  let socket = null;
  let recognition = null;
  let isRecording = false;

  // Initialize WebSocket Connection
  function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    updateStatus('disconnected', 'Connecting...');
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      updateStatus('connected', 'Online');
      appendLog('system', 'SYS', 'Connected to Ghost Pilot backend.');
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleServerMessage(data);
      } catch (err) {
        appendLog('system', 'SYS', `Raw message: ${event.data}`);
      }
    };

    socket.onclose = () => {
      updateStatus('disconnected', 'Offline (Reconnecting...)');
      appendLog('error', 'ERR', 'Connection lost. Retrying in 3 seconds...');
      setTimeout(initWebSocket, 3000);
    };

    socket.onerror = (err) => {
      console.error('WebSocket Error:', err);
    };
  }

  function updateStatus(state, text) {
    connectionStatus.className = `status-pill ${state}`;
    statusText.textContent = text;
  }

  // Handle incoming server messages
  function handleServerMessage(data) {
    const msg = data.message || '';
    switch (data.type) {
      case 'user':
        appendLog('user', 'USER', msg);
        break;
      case 'status':
        appendLog('status', 'INFO', msg);
        break;
      case 'tool_start':
        appendLog('tool', 'TOOL', msg);
        break;
      case 'tool_end':
        appendLog('result', 'DONE', msg);
        break;
      case 'response':
        appendLog('resp', 'AI', msg);
        break;
      case 'error':
        appendLog('error', 'ERR', msg);
        break;
      default:
        appendLog('system', 'SYS', msg);
    }
  }

  // Log Append Helper
  function appendLog(type, tag, text) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;

    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];

    entry.innerHTML = `
      <span class="timestamp">[${timeStr}]</span>
      <span class="tag tag-${type}">${tag}</span>
      <span class="message-content"></span>
    `;
    entry.querySelector('.message-content').textContent = text;

    logTerminal.appendChild(entry);
    logTerminal.scrollTop = logTerminal.scrollHeight;
  }

  // Web Speech API Initialization
  function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      micStatus.textContent = 'Speech recognition not supported in this browser.';
      micBtn.disabled = true;
      appendLog('error', 'ERR', 'Web Speech API is not supported in this browser. Please use text input.');
      return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'ru-RU'; // Default to Russian, speech recognition will transcribe Russian/English

    recognition.onstart = () => {
      isRecording = true;
      micBtn.classList.add('recording');
      updateStatus('listening', 'Listening...');
      micStatus.textContent = 'Listening to voice command...';
      appendLog('status', 'MIC', 'Microphone active. Listening...');
    };

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      textInput.value = transcript;
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      let errMsg = `Speech error: ${event.error}`;
      if (event.error === 'service-not-allowed' || event.error === 'not-allowed') {
        errMsg = `Microphone access or Speech Recognition service is blocked by browser/OS permissions (error: ${event.error}). Please enable microphone access in browser settings or type commands in the text box below.`;
      }
      micStatus.textContent = errMsg;
      appendLog('error', 'MIC_ERR', errMsg);
      stopRecording();
    };

    recognition.onend = () => {
      stopRecording();
      const finalCommand = textInput.value.strip ? textInput.value.strip() : textInput.value.trim();
      if (finalCommand) {
        sendCommand(finalCommand);
        textInput.value = '';
      }
    };
  }

  function toggleRecording() {
    if (!recognition) return;

    if (isRecording) {
      recognition.stop();
    } else {
      textInput.value = '';
      try {
        recognition.start();
      } catch (e) {
        console.error('Failed to start recognition:', e);
      }
    }
  }

  function stopRecording() {
    isRecording = false;
    micBtn.classList.remove('recording');
    if (socket && socket.readyState === WebSocket.OPEN) {
      updateStatus('connected', 'Online');
    }
    micStatus.textContent = 'Click microphone to speak';
  }

  // Send Command Handler
  function sendCommand(text) {
    if (!text) return;

    if (!socket || socket.readyState !== WebSocket.OPEN) {
      appendLog('error', 'ERR', 'WebSocket is not connected. Cannot send command.');
      return;
    }

    socket.send(JSON.stringify({ text }));
  }

  // Event Listeners
  micBtn.addEventListener('click', toggleRecording);

  textForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const command = textInput.value.trim();
    if (command) {
      sendCommand(command);
      textInput.value = '';
    }
  });

  clearLogsBtn.addEventListener('click', () => {
    logTerminal.innerHTML = '';
    appendLog('system', 'SYS', 'Console logs cleared.');
  });

  // Start initialization
  initWebSocket();
  initSpeechRecognition();
});
