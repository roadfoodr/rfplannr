map.on('keypress', function(e){keypress(e);});

const keyHash = 'H';
const keyDelete = 'D';
const keyDeleteNotVisible = 'V';
const colorSelected = 'crimson';

function deleteFromAllLayers(marker){
            allLayerGroups.forEach(function(layer){
                marker.removeFrom(layer);
            });
}


function keypress(e) {
    console.log(e.originalEvent);
    var key = e.originalEvent.key;
    console.log(key);

    if (key == keyHash) {
        var hashids = new Hashids();
        
        var ids = [];
        allMarkerGroup.eachLayer(function(marker){
            ids.push(marker.options.ID);
            });
        var hashid = hashids.encode(ids)
        
        console.log(export_url);
        window.location.replace(export_url+hashid);
    }
    
    else if (key == keyDelete) {
        allMarkerGroup.eachLayer(function(marker){
            if (marker.options.selected == 'yes'){
                deleteFromAllLayers(marker);
            }
        });
    }
        
    else if (key == keyDeleteNotVisible) {
        mapBounds = map.getBounds();
        allMarkerGroup.eachLayer(function(marker){
            if (!mapBounds.contains(marker.getLatLng()) || !map.hasLayer(marker)){
                deleteFromAllLayers(marker);
            }
        });
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
