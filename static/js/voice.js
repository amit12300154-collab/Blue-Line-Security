/**
 * Blue Line - Voice Emergency Keyword Detection
 * Uses the Web Speech Recognition API (Chrome / Edge) to listen for distress words.
 * Audio is processed by the browser's speech service and is never stored by Blue Line.
 */
const VoiceEmergencyTrigger = {
  recognition: null,
  isListening: false,
  keyword: 'help',
  // Extra distress words always active (English, Hinglish, Hindi, Punjabi)
  extraKeywords: ['help', 'sos', 'bachao', 'madad', 'बचाओ', 'मदद', 'ਬਚਾਓ', 'ਮਦਦ'],
  onKeywordDetectedCallback: null,

  init: function(keyword, onDetectCallback) {
    this.keyword = (keyword || 'help').toLowerCase().trim();
    this.onKeywordDetectedCallback = onDetectCallback;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Speech Recognition is not supported. Use Google Chrome or Microsoft Edge.");
      return false;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;   // faster reaction
    this.recognition.lang = 'en-IN';

    this.recognition.onresult = (event) => {
      const result = event.results[event.results.length - 1];
      const transcript = result[0].transcript.trim().toLowerCase();
      const words = [this.keyword, ...this.extraKeywords];
      if (words.some(w => w && transcript.includes(w))) {
        console.warn(`[Distress keyword matched] "${transcript}"`);
        if (this.onKeywordDetectedCallback) this.onKeywordDetectedCallback(transcript);
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("[Voice Listener Error]:", event.error);
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        this.isListening = false;
        alert("Microphone permission was blocked. Allow microphone access to use voice detection.");
      }
    };

    this.recognition.onend = () => {
      if (this.isListening) {            // browsers stop recognition periodically; restart
        setTimeout(() => {
          try { this.recognition.start(); } catch (e) { /* already running */ }
        }, 300);
      }
    };
    return true;
  },

  setKeyword: function(keyword) {
    this.keyword = (keyword || 'help').toLowerCase().trim();
  },

  start: function() {
    if (!this.recognition) {
      const ready = this.init(this.keyword, this.onKeywordDetectedCallback);
      if (!ready) {
        alert("Voice recognition is not supported on this browser (use Chrome or Edge).");
        return false;
      }
    }
    try {
      this.isListening = true;
      this.recognition.start();
      return true;
    } catch (e) {
      if (e && e.name === 'InvalidStateError') return true;   // already started
      this.isListening = false;
      console.error("Error starting speech recognition:", e);
      return false;
    }
  },

  stop: function() {
    this.isListening = false;
    if (this.recognition) {
      try { this.recognition.stop(); } catch (e) {}
    }
  },

  simulateVoiceTrigger: function() {
    if (this.onKeywordDetectedCallback) this.onKeywordDetectedCallback("Simulated distress keyword 'HELP'");
  }
};
