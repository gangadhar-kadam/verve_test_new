frappe.ui.form.on("Zones", "onload", function(frm) {
	if (in_list(user_roles, "Regional Pastor")){
   		 set_field_permlevel('region',1);
  	}
  	else if (in_list(user_roles, "Zonal Pastor")){
   		 set_field_permlevel('region',2);
  	}
});

cur_frm.fields_dict['zonal_hq'].get_query = function(doc) {
	if (doc.region){
  		return "select name,church_code,church_name from `tabChurches` where region='"+doc.region+"'"
  	}
  	else{
  		return "select name,church_code,church_name from `tabChurches`"
  	}
}

frappe.ui.form.on("Zones", "refresh", function(frm,dt,dn) {
    if(in_list(user_roles, "Zonal Pastor")){
      set_field_permlevel('contact_phone_no',0);
      set_field_permlevel('contact_email_id',0);
      set_field_permlevel('zone_code',1);
      set_field_permlevel('zone_name',1);
      set_field_permlevel('zonal_hq',0);
    }
});