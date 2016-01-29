// set region and zone from church group and zone trigger


cur_frm.add_fetch("church", "church_group", "church_group");
cur_frm.add_fetch("church", "region", "region");
cur_frm.add_fetch("church", "zone", "zone");
cur_frm.add_fetch("church", "zone_name", "zone_name");
cur_frm.add_fetch("church", "region_name", "region_name");
cur_frm.add_fetch("church", "church_name", "church_name");



cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");

cur_frm.add_fetch("zone", "region", "region");




frappe.ui.form.on("PCFs", "onload", function(frm) {

if(frm.doc.__islocal){
    argmnt={
             
            }

    if  (frm.doc.church){
          argmnt={
              "church": frm.doc.church, 
            }
    }

    else if  (frm.doc.church_group){
          argmnt={
              "church_group": frm.doc.church_group, 
            }
    }
    else if  (frm.doc.zone){
          argmnt={
              "zone": frm.doc.zone, 
            }
    }
    else if  (frm.doc.region){
          argmnt={
              "region": frm.doc.region, 
            }
    }


    frappe.call({
        method:"church_ministry.church_ministry.doctype.first_timer.first_timer.set_higher_values",
        args:{"args":argmnt},
        callback: function(r) {
          if (r.message){
            for (var key in r.message) {
                    cur_frm.set_value(key,r.message[key])                 
                    refresh_field(key)
                  }            
            }
          }
    });
  }

	if (in_list(user_roles, "Zonal Pastor")){
		set_field_permlevel('church_group',1);
    	set_field_permlevel('zone',1);
    	set_field_permlevel('region',2);
    }
	else if (in_list(user_roles, "Group Church Pastor")){
    	set_field_permlevel('church_group',1);
    	set_field_permlevel('zone',2);
    	set_field_permlevel('region',2);
    }
    else if(in_list(user_roles, "Church Pastor")){
  		set_field_permlevel('church',1);
  		set_field_permlevel('church_group',2);
  		set_field_permlevel('zone',2);
    	set_field_permlevel('region',2);
    }
    else if(in_list(user_roles, "PCF Leader")){
  		set_field_permlevel('church',2);
  		set_field_permlevel('church_group',2);
  		set_field_permlevel('zone',2);
    	set_field_permlevel('region',2);
  }
});