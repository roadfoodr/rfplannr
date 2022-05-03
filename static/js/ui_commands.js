map.on('keypress', function(e){keypress(e);});

const keyHome = 'H';
const keyHelp = 'h';
const keyHelp2 = '?';
const keyDelete = 'R';
const keyDeleteNotVisible = 'V';
const keyExport = 'X';
const colorSelected = 'crimson';

var deletedPopup = L.popup().setContent('0 markers removed');
function displayDeleted(btn, map){
    deletedPopup.setLatLng(map.getCenter()).openOn(map);
}

function deleteFromAllLayers(marker){
            allLayerGroups.forEach(function(layer){
                marker.removeFrom(layer);
            });
}

function uiHelp(){
    displayHelp(null, map);
}

function uiHome(){
    window.location.replace(home_url);
}

function uiExport(){
    var hashids = new Hashids();
    
    var ids = [];
    allMarkerGroup.eachLayer(function(marker){
        ids.push(marker.options.ID);
        });
    var hashid = hashids.encode(ids)
    
    window.location.replace(export_url+hashid);
}

function uiDelete(){
    var markers_deleted = 0;
    allMarkerGroup.eachLayer(function(marker){
        if (marker.options.selected == 'yes'){
            deleteFromAllLayers(marker);
            markers_deleted++;
        }
    });
    if (markers_deleted > 0){
        deletedPopup.setContent(
            `${markers_deleted} marker${markers_deleted==1 ? '':'s'} removed`);
        displayDeleted(null, map);
    }
}

function uiDeleteNotVisible(){
    var markers_deleted = 0;
    mapBounds = map.getBounds();
    allMarkerGroup.eachLayer(function(marker){
        if (!mapBounds.contains(marker.getLatLng()) || !map.hasLayer(marker)){
            deleteFromAllLayers(marker);
            markers_deleted++;
        }
    });
    if (markers_deleted > 0){
        deletedPopup.setContent(
            `${markers_deleted} marker${markers_deleted==1 ? '':'s'} removed`);
        displayDeleted(null, map);
    }
}

function keypress(e) {
    console.log(e.originalEvent);
    var key = e.originalEvent.key;

    if (key == keyHelp || key==keyHelp2) {
        uiHelp();
    }
    else if (key == keyHome) {
        uiHome();
    }
    else if (key == keyExport) {
        uiExport();
    }
    else if (key == keyDelete) {
        uiDelete();
    }
    else if (key == keyDeleteNotVisible) {
         uiDeleteNotVisible();
    }
}

function clickselect(e) {
    console.log(e);
    marker = e.target;
    if (marker.options.color == colorSelected) {
        marker.setStyle({
            color: marker.options.originalColor,
            fillColor: marker.options.originalColor,
        });
        marker.options.selected = 'no';
    }
    else{
        marker.setStyle({
            color: colorSelected,
            fillColor: colorSelected,
        });
        marker.options.selected = 'yes';
    }
}
