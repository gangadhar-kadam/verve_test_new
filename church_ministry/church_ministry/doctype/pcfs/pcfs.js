// set region and zone from church group and zone trigger


cur_frm.add_fetch("church", "church_group", "church_group");
cur_frm.add_fetch("church", "region", "region");
cur_frm.add_fetch("church", "zone", "zone");

cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");

cur_frm.add_fetch("zone", "region", "region");

/*frappe.ui.form.on("PCFs", "refresh", function(frm,dt,dn) {
    get_server_fields('set_higher_values','','',frm.doc, dt, dn, 1, function(r){
      refresh_field('region');
      refresh_field('zone');
      refresh_field('church_group');
      refresh_field('church');
    });
    if(in_list(user_roles, "PCF Leader")){
      set_field_permlevel('contact_phone_no',0);
      set_field_permlevel('contact_email_id',0);
      set_field_permlevel('pcf_code',1);
      set_field_permlevel('pcf_name',1);
    }
});*/

frappe.ui.form.on("PCFs", "onload", function(frm) {
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