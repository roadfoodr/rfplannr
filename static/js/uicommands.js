// map.on('keypress', function(){alert("You clicked the map");});
map
//    .on('click', function(e){console.log(e);})
    .on('keypress', function(e){keypress(e);});


const keyHash = 'H';
const colorSelected = 'crimson';


function keypress(e) {
    console.log(e.originalEvent);
    var key = e.originalEvent.key;
    console.log(key);

    if (key == keyHash) {
        var hashids = new Hashids();
//        console.log(hashids.encode(347, 1, 2, 3, 4));
        
        var ids = [];
        allMarkerGroup.eachLayer(function(marker){
            ids.push(marker.options.ID);
            });
        var hashid = hashids.encode(ids)
        
        console.log(export_url);
        window.location.replace(export_url+hashid);
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
