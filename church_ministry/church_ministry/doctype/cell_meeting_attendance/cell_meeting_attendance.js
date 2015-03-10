cur_frm.fields_dict["invitation_member_details"].grid.set_column_disp("email_id", 0);
cur_frm.fields_dict["invitation_member_details"].grid.set_column_disp("invitation", 0);

frappe.ui.form.on("Cell Meeting Attendance", "onload", function(frm) {
	if (in_list(user_roles, "Cell Leader")){
    set_field_permlevel('meeting_category',1);
    set_field_permlevel('senior_cell',2);
    set_field_permlevel('church_master',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('pcf',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Senior Cell Leader")){
    set_field_permlevel('meeting_category',1);
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('church_master',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('pcf',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "PCF Leader")){
    set_field_permlevel('meeting_category',1);
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('pcf',1);
    set_field_permlevel('church_master',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Church Pastor")){
    set_field_permlevel('church',0);
    // set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('pcf',1);
    set_field_permlevel('church_master',1);
    set_field_permlevel('church_group',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Group Church Pastor")){
    // set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('pcf',1);
    set_field_permlevel('church_master',1);
    set_field_permlevel('church_group',1);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Zonal Pastor")){
    // set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('pcf',1);
    set_field_permlevel('church_master',1);
    set_field_permlevel('church_group',1);
    set_field_permlevel('zone',1);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Regional Pastor")){
    // set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('pcf',1);
    set_field_permlevel('church_master',1);
    set_field_permlevel('church_group',1);
    set_field_permlevel('zone',1);
    set_field_permlevel('region',1);
  }
});