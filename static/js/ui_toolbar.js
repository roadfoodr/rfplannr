var helpContent = `
    <h3>Roadfood Planner - Keyboard commands</h3>
    <ul>
    <li><strong>left mouse click</strong>: select/deselect marker</li>
    <li><strong>shift-click and drag</strong>: zoom map to a box selection</li>
    <li><strong>${keyDelete}</strong> or <i class="fa-regular fa-trash-can"></i>: remove selected markers</li>
    <li><strong>${keyDeleteNotVisible}</strong> or <i class="fa-solid fa-trash-can"></i>: remove all markers not currently visible on map</li>
    <li><strong>${keyExport}</strong> or <i class="fa-solid fa-table-list"></i>: table view of current markers with spreadsheet export</li>
    <li><strong>${keyHelp}</strong> or <strong>${keyHelp2}</strong> or <i class="fa-solid fa-question"></i>: display this help popup</li>
    </ul>
    <ul style="list-style: none;">    
    <li>Project source code: <code>
        <a href='https://github.com/roadfoodr/rfplannr' target='_blank'>
        github.com/roadfoodr/rfplannr</a></code></li>
    </ul>
`;
var helpPopup = L.popup().setContent(helpContent);

function displayHelp(btn, map){
    helpPopup.setLatLng(map.getCenter()).openOn(map);
}

var buttons = [ L.easyButton('fa-regular fa-trash-can', uiDelete, 
                    'Remove selected markers'),
                L.easyButton('fa-solid fa-trash-can', uiDeleteNotVisible, 
                    'Remove all markers not currently visible on map'),
                L.easyButton('fa-solid fa-table-list', uiExport,
                    'Table view of current markers with spreadsheet export'),
                L.easyButton('fa-solid fa-question', displayHelp, 'Help')];

L.easyBar(buttons).addTo(map);
