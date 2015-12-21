// for setting region from zone
cur_frm.add_fetch("zone", "region", "region");

frappe.ui.form.on("Group Churches", "onload", function(frm) {
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

frappe.ui.form.on("Group Churches", "refresh", function(frm,dt,dn) {
/*    get_server_fields('set_higher_values','','',frm.doc, dt, dn, 1);
      refresh_field('region');
      refresh_field('zone');*/

    if(in_list(user_roles, "Group Church Pastor")){
      set_field_permlevel('contact_phone_no',0);
      set_field_permlevel('contact_email_id',0);
      set_field_permlevel('church_group_code',1);
      set_field_permlevel('church_group',1);
      set_field_permlevel('group_church_hq',0);
    }
});

cur_frm.fields_dict['group_church_hq'].get_query = function(doc) {
  if (doc.region){
      return "select name,church_code,church_name from `tabChurches` where region='"+doc.region+"'"
    }
    else{
      return "select name,church_code,church_name from `tabChurches`"
    }
}