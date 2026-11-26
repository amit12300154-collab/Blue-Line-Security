/**
 * Blue Line - Emergency Orchestration Module
 * SOS button / shake / voice -> countdown (cancel or change emergency type) -> REST dispatch.
 */
const EMERGENCY_TYPES = [
  ['FIRE', '🔥 Fire'], ['ROBBERY', '🕵️ Robbery'], ['THEFT', '👜 Theft'], ['ASSAULT', '🚨 Assault'],
  ['HARASSMENT', '⚠️ Harassment'], ['MEDICAL', '🩺 Medical'], ['ACCIDENT', '🚗 Accident'], ['OTHER', '❓ Other']
];

const EmergencyController = {
  countdownSeconds: 10,
  countdownInterval: null,
  currentRemaining: 10,
  isActive: false,
  pendingTriggerType: 'PANIC_BUTTON',
  pendingEmergencyType: 'OTHER',
  pendingDescription: '',
  acquiredCoords: null,
  audioCtx: null,

  init: function(defaultCountdown) {
    const n = parseInt(defaultCountdown, 10);
    if (n >= 3 && n <= 120) this.countdownSeconds = n;
  },

  beep: function(freq) {
    try {
      this.audioCtx = this.audioCtx || new (window.AudioContext || window.webkitAudioContext)();
      const o = this.audioCtx.createOscillator(), g = this.audioCtx.createGain();
      o.frequency.value = freq || 880; g.gain.value = 0.12;
      o.connect(g); g.connect(this.audioCtx.destination);
      o.start(); o.stop(this.audioCtx.currentTime + 0.12);
    } catch (e) { /* audio blocked - ignore */ }
  },

  renderTypeChips: function() {
    const box = document.getElementById('countdownTypeChips');
    if (!box) return;
    box.innerHTML = '';
    EMERGENCY_TYPES.forEach(([value, label]) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'btn btn-sm ' + (value === this.pendingEmergencyType ? 'btn-warning fw-bold' : 'btn-outline-light');
      b.textContent = label;
      b.addEventListener('click', () => { this.pendingEmergencyType = value; this.renderTypeChips(); });
      box.appendChild(b);
    });
  },

  /** Step 1: SOS button opens the emergency-type modal. */
  startManualSosFlow: function() {
    if (this.isActive) return;
    this.beep(660);   // unlocks audio on iOS/Chrome (user gesture)
    const modalEl = document.getElementById('emergencyTypeModal');
    if (modalEl && window.bootstrap) {
      bootstrap.Modal.getOrCreateInstance(modalEl).show();
    } else {
      this.initiateEmergencyCountdown('PANIC_BUTTON', 'OTHER', 'Emergency triggered via SOS button');
    }
  },

  /** Step 2: countdown with cancel window. Ignores re-triggers while one is running. */
  initiateEmergencyCountdown: function(triggerType, emergencyType, description) {
    if (this.isActive) return;
    this.isActive = true;
    this.pendingTriggerType = triggerType || 'PANIC_BUTTON';
    this.pendingEmergencyType = emergencyType || 'OTHER';
    this.pendingDescription = description || '';
    this.acquiredCoords = null;

    LocationManager.getCurrentPosition()
      .then(coords => { this.acquiredCoords = coords; })
      .catch(err => console.warn("Could not pre-acquire GPS:", err.message));

    const overlay = document.getElementById('countdownOverlay');
    const numDisplay = document.getElementById('countdownNumber');
    const triggerLabel = document.getElementById('countdownTriggerLabel');

    if (!overlay || !numDisplay) {
      this.executeEmergencyDispatch();
      return;
    }

    this.currentRemaining = this.countdownSeconds;
    numDisplay.textContent = this.currentRemaining;
    if (triggerLabel) {
      let label = "Emergency Trigger Activated";
      if (triggerType === 'IMPACT_DETECTED') label = "Phone Shake Detected!";
      if (triggerType === 'VOICE_TRIGGER') label = "Emergency Word Heard!";
      triggerLabel.textContent = label;
    }
    this.renderTypeChips();
    overlay.classList.remove('d-none');
    if ('vibrate' in navigator) navigator.vibrate([300, 100, 300]);
    this.beep();

    clearInterval(this.countdownInterval);
    this.countdownInterval = setInterval(() => {
      this.currentRemaining--;
      numDisplay.textContent = Math.max(this.currentRemaining, 0);
      this.beep(this.currentRemaining <= 3 ? 1100 : 880);
      if (this.currentRemaining <= 0) {
        clearInterval(this.countdownInterval);
        this.executeEmergencyDispatch();
      }
    }, 1000);
  },

  /** "I am safe - cancel" */
  cancelCountdown: function() {
    clearInterval(this.countdownInterval);
    this.isActive = false;
    const overlay = document.getElementById('countdownOverlay');
    if (overlay) overlay.classList.add('d-none');
    if ('vibrate' in navigator) navigator.vibrate(0);
    alert("Emergency alert cancelled. You are safe.");
  },

  /** Final step: send alert to backend. */
  executeEmergencyDispatch: async function() {
    clearInterval(this.countdownInterval);
    const overlay = document.getElementById('countdownOverlay');
    if (overlay) overlay.classList.add('d-none');
    this.isActive = true;

    let lat = null, lon = null, acc = null;
    let coords = this.acquiredCoords;
    if (!coords) {
      try { coords = await LocationManager.getCurrentPosition(); }
      catch (e) { console.warn("Dispatching without live coordinates:", e.message); }
    }
    if (coords) { lat = coords.latitude; lon = coords.longitude; acc = coords.accuracy; }

    const payload = {
      trigger_type: this.pendingTriggerType,
      emergency_type: this.pendingEmergencyType,
      description: this.pendingDescription,
      latitude: lat, longitude: lon, accuracy: acc
    };

    try {
      const response = await fetch('/api/emergency/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (result.success || (result.data && result.data.alert)) {
        window.location.href = '/emergency/';
        return;
      }
      alert("Alert dispatch notice: " + result.message);
    } catch (err) {
      console.error("Failed to dispatch emergency alert:", err);
      alert("Network error sending the alert. Please call 112 directly.");
    }
    this.isActive = false;
  }
};
