// for setting region from zone
cur_frm.add_fetch("zone", "region", "region");

frappe.ui.form.on("Group Church Master", "onload", function(frm) {
	if (in_list(user_roles, "Regional Pastor")){
    	set_field_permlevel('region',1);
  	}
 	else if (in_list(user_roles, "Zonal Pastor")){
  		set_field_permlevel('zone',1);
    	set_field_permlevel('region',2);
    }
    else if (in_list(user_roles, "Group Church Pastor")){
   		set_field_permlevel('zone',2);
    	set_field_permlevel('region',2);
  	}
});

frappe.ui.form.on("Group Church Master", "refresh", function(frm,dt,dn) {
    get_server_fields('set_higher_values','','',frm.doc, dt, dn, 1);
      refresh_field('region');
      refresh_field('zone');
});