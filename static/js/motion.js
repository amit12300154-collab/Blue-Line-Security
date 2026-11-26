/**
 * Blue Line - Motion and Impact Detection Module
 * Monitors DeviceMotionEvent and triggers the emergency countdown when the phone is shaken hard
 * (several strong acceleration spikes within a short window) so a single accidental bump is ignored.
 */
const MotionDetector = {
  isEnabled: false,
  threshold: 25.0,        // m/s^2 acceleration magnitude that counts as one spike
  requiredShakes: 2,      // spikes needed inside shakeWindowMs
  shakeWindowMs: 1500,
  spikeDebounceMs: 200,
  cooldownMs: 15000,
  lastTriggerTime: 0,
  lastSpikeTime: 0,
  spikeTimes: [],
  onImpactDetectedCallback: null,
  _handler: null,
  _listening: false,

  init: function(thresholdValue, onImpactCallback) {
    if (thresholdValue) this.threshold = parseFloat(thresholdValue);
    this.onImpactDetectedCallback = onImpactCallback;

    const savedThreshold = parseFloat(localStorage.getItem('blueline_impact_threshold'));
    if (!isNaN(savedThreshold)) this.threshold = savedThreshold;
  },

  enable: async function() {
    if (typeof DeviceMotionEvent === 'undefined') {
      alert("Motion sensors are not supported on this device/browser. Use the 'Simulate Impact' button for demo.");
      return false;
    }

    // iOS 13+ needs a permission prompt triggered by a user gesture
    if (typeof DeviceMotionEvent.requestPermission === 'function') {
      try {
        const permission = await DeviceMotionEvent.requestPermission();
        if (permission !== 'granted') {
          alert("Motion sensor permission denied.");
          return false;
        }
      } catch (err) {
        console.warn("Motion permission needs a tap on the toggle:", err);
        return false;
      }
    }

    if (!this._listening) {
      this._handler = this.handleMotionEvent.bind(this);
      window.addEventListener('devicemotion', this._handler, true);
      this._listening = true;
    }
    this.isEnabled = true;
    localStorage.setItem('blueline_impact_enabled', 'true');
    return true;
  },

  disable: function() {
    if (this._listening && this._handler) {
      window.removeEventListener('devicemotion', this._handler, true);
    }
    this._listening = false;
    this.isEnabled = false;
    this.spikeTimes = [];
    localStorage.setItem('blueline_impact_enabled', 'false');
  },

  setThreshold: function(newThreshold) {
    this.threshold = parseFloat(newThreshold);
    localStorage.setItem('blueline_impact_threshold', newThreshold);
  },

  handleMotionEvent: function(event) {
    if (!this.isEnabled) return;

    const acc = event.accelerationIncludingGravity || event.acceleration;
    if (!acc || acc.x === null || acc.x === undefined) return;

    const magnitude = Math.sqrt((acc.x || 0) ** 2 + (acc.y || 0) ** 2 + (acc.z || 0) ** 2);
    const now = Date.now();
    if (magnitude <= this.threshold || now - this.lastSpikeTime < this.spikeDebounceMs) return;

    this.lastSpikeTime = now;
    this.spikeTimes = this.spikeTimes.filter(t => now - t < this.shakeWindowMs);
    this.spikeTimes.push(now);

    if (this.spikeTimes.length >= this.requiredShakes && now - this.lastTriggerTime > this.cooldownMs) {
      this.lastTriggerTime = now;
      this.spikeTimes = [];
      console.warn(`[Shake Detected] Peak ${magnitude.toFixed(1)} m/s² > ${this.threshold}`);
      if (this.onImpactDetectedCallback) this.onImpactDetectedCallback(magnitude);
    }
  },

  /** Simulation helper for desktop demos where no accelerometer exists. */
  simulateImpact: function() {
    if (this.onImpactDetectedCallback) this.onImpactDetectedCallback(32.5);
  }
};
