cur_frm.fields_dict["invitation_member_details"].grid.set_column_disp("email_id", 0);
cur_frm.fields_dict["invitation_member_details"].grid.set_column_disp("invitation", 0);

cur_frm.add_fetch("cell", "pcf", "pcf");
cur_frm.add_fetch("cell", "church", "church");
cur_frm.add_fetch("cell", "church_group", "church_group");
cur_frm.add_fetch("cell", "region", "region");
cur_frm.add_fetch("cell", "zone", "zone");
cur_frm.add_fetch("cell", "senior_cell", "senior_cell");

cur_frm.add_fetch("senior_cell", "pcf", "pcf");
cur_frm.add_fetch("senior_cell", "church", "church");
cur_frm.add_fetch("senior_cell", "church_group", "church_group");
cur_frm.add_fetch("senior_cell", "region", "region");
cur_frm.add_fetch("senior_cell", "zone", "zone");


cur_frm.add_fetch("pcf", "church", "church");
cur_frm.add_fetch("pcf", "church_group", "church_group");
cur_frm.add_fetch("pcf", "region", "region");
cur_frm.add_fetch("pcf", "zone", "zone");
cur_frm.add_fetch("pcf", "senior_cell", "senior_cell");

cur_frm.add_fetch("church", "church_group", "church_group");
cur_frm.add_fetch("church", "region", "region");
cur_frm.add_fetch("church", "zone", "zone");

cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");

cur_frm.add_fetch("zone", "region", "region");

frappe.ui.form.on("Attendance Record", "refresh", function(frm,dt,dn) {
    // get_server_fields('set_higher_values','','',frm.doc, dt, dn, 1, function(r){
    //   refresh_field('region');
    //   refresh_field('zone');
    //   refresh_field('church_group');
    //   refresh_field('church');
    //   refresh_field('pcf');
    //   refresh_field('senior_cell');
    //   refresh_field('cell');
    //  });

    if (frm.doc.meeting_category=="Cell Meeting"){
      unhide_field('meeting_subject')
      hide_field('meeting_sub')
    }
    else if(frm.doc.meeting_category=="Church Meeting"){
      hide_field('meeting_subject')
      unhide_field('meeting_sub')
    }
});

cur_frm.fields_dict['cell'].get_query = function(doc) {
  if (doc.church){
    return "select name,cell_code,cell_name from `tabCell Master` where church='"+doc.church+"'"
  }
  else{
    return "select name,cell_code,cell_name from `tabCell Master`"
  }
}

frappe.ui.form.on("Attendance Record", "validate", function(frm,doc) {
   if (frm.doc.meeting_category=="Cell Meeting"){
    if (!frm.doc.meeting_subject){
      msgprint("Please Enter Meeting Subject before save document.! ");
      throw "Enter Meeting Subject.!"
    }
   }
   else if (frm.doc.meeting_category=="Church Meeting"){
    if (!frm.doc.meeting_sub){
      msgprint("Please Enter Meeting Subject before save document.! ");
      throw "Enter Meeting Subject.!"
    }
   }
});

frappe.ui.form.on("Attendance Record", "meeting_category", function(frm,doc) {
  if (frm.doc.meeting_category=="Cell Meeting"){
    unhide_field('meeting_subject')
    hide_field('meeting_sub')
    unhide_field('cell')
    hide_field('church')
  }
  else if(frm.doc.meeting_category=="Church Meeting"){
    hide_field('meeting_subject')
    unhide_field('meeting_sub')
    unhide_field('church')
  }
});

frappe.ui.form.on("Attendance Record", "onload", function(frm) {
  if (frm.doc.__islocal){
    unhide_field('meeting_subject')
    hide_field('meeting_sub')
    unhide_field('cell')
    // hide_field('church')
  }

  if(frm.doc.__islocal && frm.doc.cell ){   
    argmnt={
              "name": frm.doc.cell  
            }
 
    frappe.call({
        method:"church_ministry.church_ministry.doctype.first_timer.first_timer.set_higher_values",
        args:{"args":argmnt},
        callback: function(r) {
          if (r.message){
            frm.doc.region=r.message.region
            frm.doc.zone=r.message.zone
            frm.doc.church_group=r.message.church_group
            frm.doc.church=r.message.church
            frm.doc.pcf=r.message.pcf
            frm.doc.senior_cell=r.message.senior_cell

            refresh_field('region');              
            refresh_field('zone');
            refresh_field('church_group');              
            refresh_field('church');
            refresh_field('pcf');              
            refresh_field('senior_cell');
          }
        }
      });
  }
  
	if (in_list(user_roles, "Cell Leader")){
    set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',2);
    set_field_permlevel('church',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('pcf',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Senior Cell Leader")){
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('church',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('pcf',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "PCF Leader")){
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',1);
    set_field_permlevel('church',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Church Pastor")){
    set_field_permlevel('church',0);
    // set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',1);
    set_field_permlevel('church_group',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Group Church Pastor")){
    // set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',1);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Zonal Pastor")){
    // set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',0);
    set_field_permlevel('zone',1);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Regional Pastor")){
    // set_field_permlevel('cell',1);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',0);
    set_field_permlevel('zone',0);
    set_field_permlevel('region',1);
  }
  else if(in_list(user_roles, "System Manager")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',0);
    set_field_permlevel('zone',0);
    set_field_permlevel('region',0);
  }
});

cur_frm.fields_dict['cell'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Cell Master',
      'senior_cell' : doc.senior_cell,
      'pcf' : doc.pcf,
      'church' : doc.church,
      'church_group' : doc.church_group,
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['senior_cell'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Senior Cell Master',
      'pcf' : doc.pcf,
      'church' : doc.church,
      'church_group' : doc.church_group,
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['pcf'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'PCF Master',
      'church' : doc.church,
      'church_group' : doc.church_group,
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['church'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Church Master',
      'church_group' : doc.church_group,
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}
cur_frm.fields_dict['church_group'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Group Church Master',
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['zone'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Zone Master',
      'region' : doc.region
    }
  }
}