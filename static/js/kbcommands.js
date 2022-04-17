// map.on('keypress', function(){alert("You clicked the map");});
map
//    .on('click', function(e){console.log(e);})
    .on('keypress', function(e){keypress(e);});


function keypress(e) {
    console.log(e.originalEvent);
    var key = e.originalEvent.key;
    console.log(key);

    if (key == 'H') {
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



/*    
    if (event.originalEvent.ctrlKey) {
    // handle ctrl + click ...

*/
