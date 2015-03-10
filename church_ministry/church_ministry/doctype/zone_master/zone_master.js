frappe.ui.form.on("Zone Master", "onload", function(frm) {
	if (in_list(user_roles, "Regional Pastor")){
   		 set_field_permlevel('region',1);
  	}
  	else if (in_list(user_roles, "Zonal Pastor")){
   		 set_field_permlevel('region',2);
  	}
});