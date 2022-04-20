var helpContent = `
    <h3>Roadfood Planner - Keyboard commands</h3>
    <ul>
    <li><strong>${keyHelp}</strong> or <strong>${keyHelp2}</strong>: display this help popup</li>
    <li><strong>left mouse click</strong>: select/deselect marker</li>
    <li><strong>shift-click and drag</strong>: zoom map to a box selection</li>
    <li><strong>${keyDelete}</strong>: remove selected markers</li>
    <li><strong>${keyDeleteNotVisible}</strong>: remove all markers not currently visible on map</li>
    <li><strong>${keyExport}</strong>: export markers to a spreadsheet file</li>
    </ul>
`;

function displayHelp(btn, map){
    helpPopup.setLatLng(map.getCenter()).openOn(map);
}

var helpPopup = L.popup().setContent(helpContent);
L.easyButton('<strong>?</strong>', displayHelp).addTo(map);
