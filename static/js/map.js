/**
 * Blue Line - Leaflet Map Integration Module
 * Renders OpenStreetMap, user position markers, police station pins, accuracy circles, and breadcrumb trails.
 */
const MapManager = {
  map: null,
  userMarker: null,
  policeMarker: null,
  accuracyCircle: null,
  trailPolyline: null,
  trailCoordinates: [],

  init: function(containerId, initialLat, initialLon, zoom = 14) {
    if (!document.getElementById(containerId)) {
      console.warn(`Map container #${containerId} not found.`);
      return null;
    }

    const defaultLat = initialLat || 28.6139; // Default New Delhi coordinates
    const defaultLon = initialLon || 77.2090;

    // Initialize Leaflet map
    this.map = L.map(containerId).setView([defaultLat, defaultLon], zoom);

    // OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    }).addTo(this.map);

    // Initialize polyline for GPS breadcrumb trajectory
    this.trailPolyline = L.polyline([], {
      color: '#e74c3c',
      weight: 4,
      opacity: 0.8,
      dashArray: '6, 8'
    }).addTo(this.map);

    return this.map;
  },

  updateUserMarker: function(lat, lon, accuracy = null, popupText = "Your Current Location") {
    if (!this.map) return;

    const latlng = [lat, lon];

    // User marker custom pulsing icon
    const userIcon = L.divIcon({
      className: 'user-location-pin',
      html: `<div style="
        width: 22px;
        height: 22px;
        background: #e74c3c;
        border: 3px solid #ffffff;
        border-radius: 50%;
        box-shadow: 0 0 12px rgba(231, 76, 60, 0.8);
      "></div>`,
      iconSize: [22, 22],
      iconAnchor: [11, 11]
    });

    if (!this.userMarker) {
      this.userMarker = L.marker(latlng, { icon: userIcon }).addTo(this.map);
    } else {
      this.userMarker.setLatLng(latlng);
    }
    this.userMarker.bindPopup(`<b>🚨 EMERGENCY LOCATION</b><br>${popupText}`).openPopup();

    // Accuracy Circle
    if (accuracy) {
      if (!this.accuracyCircle) {
        this.accuracyCircle = L.circle(latlng, {
          radius: accuracy,
          color: '#e74c3c',
          fillColor: '#e74c3c',
          fillOpacity: 0.15,
          weight: 1
        }).addTo(this.map);
      } else {
        this.accuracyCircle.setLatLng(latlng);
        this.accuracyCircle.setRadius(accuracy);
      }
    }

    // Append to breadcrumb trail
    this.trailCoordinates.push(latlng);
    this.trailPolyline.setLatLngs(this.trailCoordinates);

    this.map.panTo(latlng);
  },

  setPoliceStationMarker: function(lat, lon, name, address, phone = null, distance = null) {
    if (!this.map) return;

    const policeIcon = L.divIcon({
      className: 'police-station-pin',
      html: `<div style="
        width: 26px;
        height: 26px;
        background: #1e3c72;
        color: #fff;
        border: 3px solid #fff;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
      ">🚔</div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    });

    const distStr = distance ? `<br><b>Distance:</b> ${distance}` : '';
    const phoneStr = phone ? `<br><b>Phone:</b> ${phone}` : '';
    const popupContent = `
      <div style="min-width: 180px;">
        <h6 style="margin: 0 0 5px 0; color: #1e3c72;">🚔 ${name}</h6>
        <small style="color: #666;">${address}</small>
        ${distStr}
        ${phoneStr}
        <br><span class="badge bg-warning text-dark mt-1" style="font-size: 0.65rem;">DEMO / SIMULATION</span>
      </div>
    `;

    if (!this.policeMarker) {
      this.policeMarker = L.marker([lat, lon], { icon: policeIcon }).addTo(this.map);
    } else {
      this.policeMarker.setLatLng([lat, lon]);
    }
    this.policeMarker.bindPopup(popupContent);
  },

  drawBreadcrumbHistory: function(breadcrumbs) {
    if (!this.map || !Array.isArray(breadcrumbs) || breadcrumbs.length === 0) return;

    const latlngs = breadcrumbs.map(b => [b.latitude, b.longitude]);
    this.trailCoordinates = latlngs;
    this.trailPolyline.setLatLngs(latlngs);

    if (latlngs.length > 0) {
      this.map.fitBounds(this.trailPolyline.getBounds(), { padding: [50, 50] });
    }
  }
};
