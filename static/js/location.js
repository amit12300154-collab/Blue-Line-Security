/**
 * Blue Line - Location Service Module
 * Handles HTML5 Geolocation API, error handling, live watchPosition, and coordinate throttling.
 */
const LocationManager = {
  currentCoords: null,
  watchId: null,
  lastSendTime: 0,
  sendIntervalMs: 5000, // Send updates at most once every 5 seconds

  /**
   * Acquire single current GPS location.
   */
  getCurrentPosition: function() {
    return new Promise((resolve, reject) => {
      if (!('geolocation' in navigator)) {
        reject(new Error("Geolocation is not supported by your browser."));
        return;
      }

      const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 5000
      };

      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.currentCoords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: position.timestamp
          };
          resolve(this.currentCoords);
        },
        (error) => {
          let message = "Unable to retrieve location.";
          switch (error.code) {
            case error.PERMISSION_DENIED:
              message = "Location permission was denied. Please allow location access for emergency dispatch.";
              break;
            case error.POSITION_UNAVAILABLE:
              message = "Location information is unavailable on this device.";
              break;
            case error.TIMEOUT:
              message = "Location request timed out. Please try again or check GPS settings.";
              break;
          }
          reject(new Error(message));
        },
        options
      );
    });
  },

  /**
   * Start live GPS watch for continuous tracking during active alert.
   */
  startLiveTracking: function(alertId, onUpdateCallback) {
    if (!('geolocation' in navigator)) {
      console.warn("Geolocation API unavailable for live tracking.");
      return;
    }

    if (this.watchId !== null) {
      navigator.geolocation.clearWatch(this.watchId);
    }

    const options = {
      enableHighAccuracy: true,
      maximumAge: 2000,
      timeout: 10000
    };

    this.watchId = navigator.geolocation.watchPosition(
      (position) => {
        this.currentCoords = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp
        };

        if (onUpdateCallback) {
          onUpdateCallback(this.currentCoords);
        }

        // Throttle sending coordinates to server
        const now = Date.now();
        if (alertId && (now - this.lastSendTime >= this.sendIntervalMs)) {
          this.lastSendTime = now;
          this.sendCoordinatesToServer(alertId, this.currentCoords);
        }
      },
      (err) => {
        console.warn("watchPosition warning:", err.message);
      },
      options
    );
  },

  /**
   * Stop tracking and clear active GPS watch.
   */
  stopLiveTracking: function() {
    if (this.watchId !== null) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
      console.log("Live GPS tracking halted.");
    }
  },

  /**
   * Dispatch location update payload to REST API.
   */
  sendCoordinatesToServer: function(alertId, coords) {
    fetch(`/api/emergency/${alertId}/location`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        latitude: coords.latitude,
        longitude: coords.longitude,
        accuracy: coords.accuracy
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        console.log("GPS breadcrumb persisted:", coords.latitude, coords.longitude);
      }
    })
    .catch(err => {
      console.error("Failed to post coordinate update:", err);
    });
  },

  /**
   * Format Google Maps navigation link.
   */
  getGoogleMapsUrl: function(lat, lon) {
    if (lat && lon) {
      return `https://www.google.com/maps?q=${lat},${lon}`;
    }
    return null;
  }
};
