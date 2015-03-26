// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.fields_dict['cell'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Cell Master',
      'senior_cell' : doc.senior_cell,
      'pcf' : doc.pcf,
      'church' : doc.church,
      'church_group' : doc.church_group,
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['senior_cell'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Senior Cell Master',
      'pcf' : doc.pcf,
      'church' : doc.church,
      'church_group' : doc.church_group,
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['pcf'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'PCF Master',
      'church' : doc.church,
      'church_group' : doc.church_group,
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['church'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Church Master',
      'church_group' : doc.church_group,
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}
cur_frm.fields_dict['church_group'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Group Church Master',
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['zone'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Zone Master',
      'region' : doc.region
    }
  }
}

frappe.ui.form.on("First Timer", "onload", function(frm,cdt, cdn) {
  if(!frm.doc.__islocal){
    set_field_permlevel('email_id',1);
  }
  else if(frm.doc.__islocal && frm.doc.cell ){   
    argmnt={
/*              "region": frm.doc.region,
              "zone": frm.doc.zone,
              "church_group": frm.doc.church_group,
              "church": frm.doc.church ,
              "pcf": frm.doc.pcf,
              "senior_cell": frm.doc.senior_cell,*/
              "name": frm.doc.cell  
            }
 
    frappe.call({
        method:"church_ministry.church_ministry.doctype.first_timer.first_timer.set_higher_values",
        args:{"args":argmnt},
        callback: function(r) {
          if (r.message){
            console.log(r.message);
            frm.doc.region=r.message.region
            frm.doc.zone=r.message.zone
            frm.doc.church_group=r.message.church_group
            frm.doc.church=r.message.church
            frm.doc.pcf=r.message.pcf
            frm.doc.senior_cell=r.message.senior_cell
            //frm.doc.cell=r.message.name
            refresh_field('region');              
            refresh_field('zone');
            refresh_field('church_group');              
            refresh_field('church');
            refresh_field('pcf');              
            refresh_field('senior_cell');
           // refresh_field('cell');
          }
        }
      });
  }

  if (in_list(user_roles, "Cell Leader")){
    set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',2);
    set_field_permlevel('church',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('pcf',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Senior Cell Leader")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('church',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('pcf',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "PCF Leader")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',1);
    set_field_permlevel('church',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Church Pastor")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',1);
    set_field_permlevel('church_group',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Group Church Pastor")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',1);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Zonal Pastor")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',0);
    set_field_permlevel('zone',1);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Regional Pastor")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',0);
    set_field_permlevel('zone',0);
    set_field_permlevel('region',1);
  }
 
  // home address map
  $( "#map-canvas" ).remove();
  $(cur_frm.get_field("address").wrapper).append('<div id="map-canvas" style="width: 425px; height: 225px;"></div>');
  
/*  // office address map
  $( "#map-canvas1" ).remove();
  $(cur_frm.get_field("office_address").wrapper).append('<div id="map-canvas1" style="width: 425px; height: 225px;"></div>');
 */  
  // display map if form is saved and have lat and lon
    if(!frm.doc.__islocal && (frm.doc.lat &&  frm.doc.lon)){
      cur_frm.cscript.create_pin_on_map(frm.doc,frm.doc.lat,frm.doc.lon);
    }  
});

frappe.ui.form.on("First Timer", "refresh", function(frm,doc,dt,dn) {
    if(!frm.doc.__islocal && frm.doc.approved) {
        frappe.call({
              method:"church_ministry.church_ministry.doctype.first_timer.first_timer.ismember",
              args:{
                      "name":frm.doc.name
              },
              callback: function(r) {
                  if (r.message=='No'){
                      frm.add_custom_button(__("Create Member"), cur_frm.cscript.create_member,frappe.boot.doctype_icons["Customer"], "btn-default");
                  }
              }
        })      
    }
    
});

frappe.ui.form.on("First Timer", "create_member", function(frm,doc) {
    frappe.model.open_mapped_doc({
      method: "church_ministry.church_ministry.doctype.first_timer.first_timer.make_member",
      frm: cur_frm
    })
});


frappe.ui.form.on("First Timer", "baptism_status", function(frm,doc) {
});

cur_frm.add_fetch("cell", "pcf", "pcf");
cur_frm.add_fetch("cell", "church", "church");
cur_frm.add_fetch("cell", "church_group", "church_group");
cur_frm.add_fetch("cell", "region", "region");
cur_frm.add_fetch("cell", "zone", "zone");
cur_frm.add_fetch("cell", "senior_cell", "senior_cell");

cur_frm.add_fetch("senior_cell", "pcf", "pcf");
cur_frm.add_fetch("senior_cell", "church", "church");
cur_frm.add_fetch("senior_cell", "church_group", "church_group");
cur_frm.add_fetch("senior_cell", "region", "region");
cur_frm.add_fetch("senior_cell", "zone", "zone");


cur_frm.add_fetch("pcf", "church", "church");
cur_frm.add_fetch("pcf", "church_group", "church_group");
cur_frm.add_fetch("pcf", "region", "region");
cur_frm.add_fetch("pcf", "zone", "zone");

cur_frm.add_fetch("church", "church_group", "church_group");
cur_frm.add_fetch("church", "region", "region");
cur_frm.add_fetch("church", "zone", "zone");

cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");

cur_frm.add_fetch("zone", "region", "region");

cur_frm.cscript.create_pin_on_map=function(doc,lat,lon){
        var latLng = new google.maps.LatLng(lat, lon);
        var map = new google.maps.Map(document.getElementById('map-canvas'), {
            zoom: 10,
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
      var input = (cur_frm.get_field("address").wrapper);
      console.log(['input',input]);
      /*var autocomplete = new google.maps.places.Autocomplete(input);
      autocomplete.bindTo('bounds', map);
      google.maps.event.addListener(autocomplete, 'place_changed', function() {
      infowindow.close();
      marker.setVisible(false);
      var place = autocomplete.getPlace();    
      var address = '';
      if (place.address_components) {
        address = [
          (place.address_components[0] && place.address_components[0].short_name || ''),
          (place.address_components[1] && place.address_components[1].short_name || ''),
          (place.address_components[2] && place.address_components[2].short_name || '')
        ].join(' ');
      }
      console.log(['place name---',place.name]);
      infowindow.setContent('<div><strong>' + place.name + '</strong><br>' + address);
      infowindow.open(map, marker);
      });*/

      geocoder.geocode( { 'address': doc.address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
          doc.address=results[0].formatted_address;
          refresh_field('address');
          var latLng = new google.maps.LatLng(results[0].geometry.location.lat(), results[0].geometry.location.lng());

          var map = new google.maps.Map(document.getElementById('map-canvas'), {
              zoom: 10,
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


