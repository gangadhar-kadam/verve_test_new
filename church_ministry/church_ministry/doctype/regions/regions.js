frappe.ui.form.on("Regions", "refresh", function(frm,dt,dn) {
    if(in_list(user_roles, "Regional Pastor")){
      set_field_permlevel('contact_phone_no',0);
      set_field_permlevel('contact_email_id',0);
      set_field_permlevel('region_code',1);
      set_field_permlevel('region_name',1);
    }
});