// set region and zone from church group and zone trigger
cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");
cur_frm.add_fetch("zone", "region", "region");

frappe.ui.form.on("Church Master", "email_id", function(frm,dt,dn) {
   var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
   check=re.test(frm.doc.email_id)
   if(check==false)
   {
        cur_frm.set_value("email_id", '')
        msgprint("Please Enter valid Email Id..! ");
        throw "Please Enter Correct Email ID.!"
   }
});

frappe.ui.form.on("Church Master", "refresh", function(frm,dt,dn) {
    get_server_fields('set_higher_values','','',frm.doc, dt, dn, 1, function(r){
      refresh_field('region');
      refresh_field('zone');
      refresh_field('church_group');
    });
});

frappe.ui.form.on("Church Master", "onload", function(frm) {
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
});
