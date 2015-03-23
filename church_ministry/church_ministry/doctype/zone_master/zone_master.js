frappe.ui.form.on("Zone Master", "onload", function(frm) {
	if (in_list(user_roles, "Regional Pastor")){
   		 set_field_permlevel('region',1);
  	}
  	else if (in_list(user_roles, "Zonal Pastor")){
   		 set_field_permlevel('region',2);
  	}
});

cur_frm.fields_dict['zonal_hq'].get_query = function(doc) {
	if (doc.region){
  		return "select name,church_code,church_name from `tabChurch Master` where region='"+doc.region+"'"
  	}
  	else{
  		return "select name,church_code,church_name from `tabChurch Master`"
  	}
}