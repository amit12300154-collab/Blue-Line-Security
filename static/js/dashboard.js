/**
 * Blue Line - User Dashboard Controller
 * Connects sensors, UI widgets, SOS triggers, and simulation actions.
 */
document.addEventListener('DOMContentLoaded', () => {
  console.log("Blue Line Dashboard Controller Initialized");

  // Read config from data attributes or defaults
  const dashboardContainer = document.getElementById('dashboardContainer');
  const impactThreshold = dashboardContainer ? dashboardContainer.dataset.impactThreshold : 25.0;
  const countdownSeconds = dashboardContainer ? dashboardContainer.dataset.countdown : 10;

  // 1. Initialize Emergency Controller
  // User-saved countdown (Settings page) overrides the server default
  const savedCountdown = parseInt(localStorage.getItem('blueline_countdown_sec'), 10);
  EmergencyController.init(savedCountdown >= 3 && savedCountdown <= 120 ? savedCountdown : countdownSeconds);

  // 2. Initialize Motion Detector
  MotionDetector.init(impactThreshold, (magnitude) => {
    console.warn("Impact trigger triggered with magnitude:", magnitude);
    EmergencyController.initiateEmergencyCountdown(
      'IMPACT_DETECTED',
      'ACCIDENT',
      `Automatic trigger: Sudden phone shake / impact detected (${magnitude.toFixed(1)} m/s²)`
    );
  });

  // 3. Initialize Voice Detection
  VoiceEmergencyTrigger.init(localStorage.getItem('blueline_voice_keyword') || 'help', (transcript) => {
    console.warn("Voice trigger detected keyword 'HELP' in phrase:", transcript);
    EmergencyController.initiateEmergencyCountdown(
      'VOICE_TRIGGER',
      'OTHER',
      `Automatic trigger: Voice distress keyword 'HELP' detected ("${transcript}")`
    );
  });

  // Check saved state for impact sensor
  const impactToggle = document.getElementById('impactToggle');
  if (impactToggle) {
    impactToggle.checked = localStorage.getItem('blueline_impact_enabled') === 'true';
    if (impactToggle.checked) {
      MotionDetector.enable().then(ok => {
        if (!ok) { impactToggle.checked = false; localStorage.setItem('blueline_impact_enabled', 'false'); }
        updateSensorStatusLabels();
      });
    }

    impactToggle.addEventListener('change', async (e) => {
      if (e.target.checked) {
        const success = await MotionDetector.enable();
        if (!success) e.target.checked = false;
      } else {
        MotionDetector.disable();
      }
      updateSensorStatusLabels();
    });
  }

  // Check saved state for voice trigger
  const voiceToggle = document.getElementById('voiceToggle');
  if (voiceToggle) {
    voiceToggle.checked = localStorage.getItem('blueline_voice_enabled') === 'true';
    if (voiceToggle.checked) {
      if (!VoiceEmergencyTrigger.start()) voiceToggle.checked = false;
      updateSensorStatusLabels();
    }

    voiceToggle.addEventListener('change', (e) => {
      if (e.target.checked) {
        const success = VoiceEmergencyTrigger.start();
        if (success) {
          localStorage.setItem('blueline_voice_enabled', 'true');
        } else {
          e.target.checked = false;
        }
      } else {
        VoiceEmergencyTrigger.stop();
        localStorage.setItem('blueline_voice_enabled', 'false');
      }
      updateSensorStatusLabels();
    });
  }

  // Manual SOS button click
  const sosBtn = document.getElementById('btnSos');
  if (sosBtn) {
    sosBtn.addEventListener('click', () => {
      EmergencyController.startManualSosFlow();
    });
  }

  // Cancel Countdown button
  const btnCancelCountdown = document.getElementById('btnCancelCountdown');
  if (btnCancelCountdown) {
    btnCancelCountdown.addEventListener('click', () => {
      EmergencyController.cancelCountdown();
    });
  }

  // Send Immediately button
  const btnSendNowCountdown = document.getElementById('btnSendNowCountdown');
  if (btnSendNowCountdown) {
    btnSendNowCountdown.addEventListener('click', () => {
      EmergencyController.executeEmergencyDispatch();
    });
  }

  // Modal Confirm SOS button
  const btnConfirmSosModal = document.getElementById('btnConfirmSosModal');
  if (btnConfirmSosModal) {
    btnConfirmSosModal.addEventListener('click', () => {
      const emergencyType = document.getElementById('modalEmergencyType').value;
      const description = document.getElementById('modalEmergencyDescription').value.trim()
        || 'Emergency triggered via SOS button';

      // Close modal
      const modalEl = document.getElementById('emergencyTypeModal');
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();

      // Launch countdown
      EmergencyController.initiateEmergencyCountdown('PANIC_BUTTON', emergencyType, description);
    });
  }

  // Simulation buttons for presentation/viva
  const btnSimulateImpact = document.getElementById('btnSimulateImpact');
  if (btnSimulateImpact) {
    btnSimulateImpact.addEventListener('click', () => {
      MotionDetector.simulateImpact();
    });
  }

  const btnSimulateVoice = document.getElementById('btnSimulateVoice');
  if (btnSimulateVoice) {
    btnSimulateVoice.addEventListener('click', () => {
      VoiceEmergencyTrigger.simulateVoiceTrigger();
    });
  }

  function updateSensorStatusLabels() {
    const motionStatusPill = document.getElementById('motionStatusPill');
    if (motionStatusPill) {
      if (MotionDetector.isEnabled) {
        motionStatusPill.className = 'sensor-pill active';
        motionStatusPill.innerHTML = '<span class="sensor-dot"></span> Impact Protection: ACTIVE';
      } else {
        motionStatusPill.className = 'sensor-pill inactive';
        motionStatusPill.innerHTML = '<span class="sensor-dot"></span> Impact Protection: OFF';
      }
    }

    const voiceStatusPill = document.getElementById('voiceStatusPill');
    if (voiceStatusPill) {
      if (VoiceEmergencyTrigger.isListening) {
        voiceStatusPill.className = 'sensor-pill active';
        voiceStatusPill.innerHTML = '<span class="sensor-dot"></span> Voice Listener: ACTIVE';
      } else {
        voiceStatusPill.className = 'sensor-pill inactive';
        voiceStatusPill.innerHTML = '<span class="sensor-dot"></span> Voice Listener: OFF';
      }
    }
  }

  updateSensorStatusLabels();
});
