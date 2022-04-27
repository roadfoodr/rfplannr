map.on('keypress', function(e){keypress(e);});

const keyHash = 'h';
const keyHelp = 'H';
const keyHelp2 = '?';
const keyDelete = 'R';
const keyDeleteNotVisible = 'V';
const keyExport = 'X';
const colorSelected = 'crimson';

function deleteFromAllLayers(marker){
            allLayerGroups.forEach(function(layer){
                marker.removeFrom(layer);
            });
}

function uiHelp(){
    displayHelp(null, map);
}

function uiExport(){
    var hashids = new Hashids();
    
    var ids = [];
    allMarkerGroup.eachLayer(function(marker){
        ids.push(marker.options.ID);
        });
    var hashid = hashids.encode(ids)
    
    console.log(export_url);
    window.location.replace(export_url+hashid);
}

function uiDelete(){
    allMarkerGroup.eachLayer(function(marker){
        if (marker.options.selected == 'yes'){
            deleteFromAllLayers(marker);
        }
    });
}

function uiDeleteNotVisible(){
    mapBounds = map.getBounds();
    allMarkerGroup.eachLayer(function(marker){
        if (!mapBounds.contains(marker.getLatLng()) || !map.hasLayer(marker)){
            deleteFromAllLayers(marker);
        }
    });
}

function keypress(e) {
    console.log(e.originalEvent);
    var key = e.originalEvent.key;
    console.log(key);

    if (key == keyHelp || key==keyHelp2) {
        uiHelp();
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
