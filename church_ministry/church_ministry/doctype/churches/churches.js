// set region and zone from church group and zone trigger
cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");
cur_frm.add_fetch("zone", "region", "region");

cur_frm.fields_dict['church_group'].get_query = function(doc) {
  if (doc.zone){
    return "select name,church_group_code,church_group from `tabGroup Churches` where zone='"+doc.zone+"'"
  }
  else{
    return "select name,church_group_code,church_group from `tabGroup Churches`"
  }
}

cur_frm.fields_dict['zone'].get_query = function(doc) {
  if (doc.region){
    return "select name from `tabZones` where region='"+doc.region+"'"
  }
  else{
    return "select name from `tabZones`"
  }
}

frappe.ui.form.on("Churches", "validate", function(frm,dt,dn) {
   var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
   check=re.test(frm.doc.email_id)
   if (frm.doc.email_id){
    if(check==false){    
      cur_frm.set_value("email_id", '')
       msgprint("Please Enter valid Email Id..!");
       throw "Please Enter Correct Email ID.!"
   }
 }  
});

/*frappe.ui.form.on("Churches", "refresh", function(frm,dt,dn) {
    get_server_fields('set_higher_values','','',frm.doc, dt, dn, 1, function(r){
      refresh_field('region');
      refresh_field('zone');
      refresh_field('church_group');
    });
     if(in_list(user_roles, "Church Pastor")){
      set_field_permlevel('phone_no',0);
      set_field_permlevel('email_id',0);
      set_field_permlevel('church_code',1);
      set_field_permlevel('church_name',1);
      set_field_permlevel('address',0);
    }
});*/

frappe.ui.form.on("Churches", "onload", function(frm) {
	if (in_list(user_roles, "Regional Pastor")){
   		set_field_permlevel('region',1);
  	}
  	else if (in_list(user_roles, "Zonal Pastor")){
  		set_field_permlevel('zone',1)
   		set_field_permlevel('region',2);
  	}
	else if (in_list(user_roles, "Group Church Pastor")){
    	set_field_permlevel('church_group',1);
    	set_field_permlevel('zone',2);
    	set_field_permlevel('region',2);
    }
    else if (in_list(user_roles, "Church Pastor")){
    	set_field_permlevel('church_group',2);
    	set_field_permlevel('zone',2);
    	set_field_permlevel('region',2);
    }

    $( "#map-canvas" ).remove();
    $(cur_frm.get_field("address").wrapper).append('<div id="map-canvas" style="width: 425px; height: 425px;"></div>');
    if(!frm.doc.__islocal && (frm.doc.lat &&  frm.doc.lon)){
      cur_frm.cscript.create_pin_on_map(frm.doc,frm.doc.lat,frm.doc.lon);
    }
});


cur_frm.cscript.create_pin_on_map=function(doc,lat,lon){
        var latLng = new google.maps.LatLng(lat, lon);
        var map = new google.maps.Map(document.getElementById('map-canvas'), {
            zoom: 16,
            center: latLng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
          });
        var marker = new google.maps.Marker({
            position: latLng,
            title: 'Point',
            map: map,
            draggable: true
          });

        updateMarkerPosition(latLng);
        geocodePosition(latLng);

        google.maps.event.addListener(marker, 'dragstart', function() {
            updateMarkerAddress('Dragging...');
        });

        google.maps.event.addListener(marker, 'drag', function() {
            updateMarkerStatus('Dragging...');
            updateMarkerPosition(marker.getPosition());
        });

        google.maps.event.addListener(marker, 'dragend', function() {
            updateMarkerStatus('Drag ended');
            geocodePosition(marker.getPosition());
          });
}

function geocodePosition(pos) {
      geocoder.geocode({
        latLng: pos
      }, function(responses) {
        if (responses && responses.length > 0) {
          updateMarkerAddress(responses[0].formatted_address);
        } else {
          if(doc.__islocal) {
            alert('Cannot determine address at this location.');
          }
        }
      });
      geocoder.geocode( { 'address': doc.address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        doc.lat=results[0].geometry.location.lat();
        doc.lon=results[0].geometry.location.lng();
        refresh_field('lat')
        refresh_field('lon')
      } 
    });
}

function updateMarkerAddress(str) {
  doc=cur_frm.doc
  doc.address= str;
  refresh_field('address');
}

function updateMarkerStatus(str) {
var s=1;
}

function updateMarkerPosition(latLng) {
  doc=cur_frm.doc
  doc.lat=latLng.lat()
  doc.lon=latLng.lng()
  refresh_field('lat')
  refresh_field('lon')
}

var geocoder = new google.maps.Geocoder();
var getMarkerUniqueId= function(lat, lng) {
    return lat + '_' + lng;
}

var getLatLng = function(lat, lng) {
    return new google.maps.LatLng(lat, lng);
};

cur_frm.cscript.address = function(doc, dt, dn){
      geocoder.geocode( { 'address': doc.address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
          doc.address=results[0].formatted_address;
          refresh_field('address');
          var latLng = new google.maps.LatLng(results[0].geometry.location.lat(), results[0].geometry.location.lng());

          var map = new google.maps.Map(document.getElementById('map-canvas'), {
              zoom: 16,
              center: latLng,
              mapTypeId: google.maps.MapTypeId.ROADMAP
            });

          var marker = new google.maps.Marker({
              position: latLng,
              title: 'Point',
              map: map,
              draggable: true
            });
          updateMarkerPosition(latLng);
          geocodePosition(latLng);

          google.maps.event.addListener(marker, 'dragend', function() {
              geocodePosition(marker.getPosition());
          });
      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
    });
}