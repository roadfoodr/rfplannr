// top, bottom, left, right = 49.382808, 24.521208, -66.945392, -124.736342
var map = L.map('map', {zoomDelta: 0.25, zoomSnap: .1})
    .fitBounds([ [49.382808, -66.945392], [24.521208, -124.736342] ]);
//    .setView([39.8283, -98.5795,], 4.5);

var OpenStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var CartoDB_Voyager = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
	subdomains: 'abcd',
	maxZoom: 20
}).addTo(map);



// https://www.section.io/engineering-education/how-to-build-a-real-time-location-tracker-using-leaflet-js/
/*
function getPosition(position) {
  console.log(position)
  lat = position.coords.latitude;
  long = position.coords.longitude;
  accuracy = position.coords.accuracy;

  console.log(
    "Your coordinate is: Lat: " +
      lat +
      " Long: " +
      long +
      " Accuracy: " +
      accuracy
  );
}

navigator.geolocation.getCurrentPosition(getPosition);
*/