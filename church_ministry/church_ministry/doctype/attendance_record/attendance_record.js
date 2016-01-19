cur_frm.fields_dict["invitation_member_details"].grid.set_column_disp("email_id", 0);
cur_frm.fields_dict["invitation_member_details"].grid.set_column_disp("invitation", 0);

cur_frm.add_fetch("cell", "pcf", "pcf");
cur_frm.add_fetch("cell", "pcf_name", "pcf_name");
cur_frm.add_fetch("cell", "church", "church");
cur_frm.add_fetch("cell", "church_name", "church_name");
cur_frm.add_fetch("cell", "church_group", "church_group");
cur_frm.add_fetch("cell", "group_church_name", "group_church_name");
cur_frm.add_fetch("cell", "region", "region");
cur_frm.add_fetch("cell", "region_name", "region_name");
cur_frm.add_fetch("cell", "zone", "zone");
cur_frm.add_fetch("cell", "zone_name", "zone_name");
cur_frm.add_fetch("cell", "senior_cell", "senior_cell");
cur_frm.add_fetch("cell", "senior_cell_name", "senior_cell_name");

cur_frm.add_fetch("senior_cell", "pcf", "pcf");
cur_frm.add_fetch("senior_cell", "church", "church");
cur_frm.add_fetch("senior_cell", "church_group", "church_group");
cur_frm.add_fetch("senior_cell", "region", "region");
cur_frm.add_fetch("senior_cell", "zone", "zone");
cur_frm.add_fetch("senior_cell", "pcf_name", "pcf_name");
cur_frm.add_fetch("senior_cell", "church_name", "church_name");
cur_frm.add_fetch("senior_cell", "group_church_name", "group_church_name");
cur_frm.add_fetch("senior_cell", "region_name", "region_name");
cur_frm.add_fetch("senior_cell", "zone_name", "zone_name");

cur_frm.add_fetch("pcf", "church", "church");
cur_frm.add_fetch("pcf", "church_group", "church_group");
cur_frm.add_fetch("pcf", "region", "region");
cur_frm.add_fetch("pcf", "zone", "zone");
cur_frm.add_fetch("pcf", "church_name", "church_name");
cur_frm.add_fetch("pcf", "group_church_name", "group_church_name");
cur_frm.add_fetch("pcf", "region_name", "region_name");
cur_frm.add_fetch("pcf", "zone_name", "zone_name");

cur_frm.add_fetch("church", "church_group", "church_group");
cur_frm.add_fetch("church", "region", "region");
cur_frm.add_fetch("church", "zone", "zone");
cur_frm.add_fetch("church", "group_church_name", "group_church_name");
cur_frm.add_fetch("church", "region_name", "region_name");
cur_frm.add_fetch("church", "zone_name", "zone_name");

cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");
cur_frm.add_fetch("church_group", "region_name", "region_name");
cur_frm.add_fetch("church_group", "zone_name", "zone_name");

cur_frm.add_fetch("zone", "region", "region");
cur_frm.add_fetch("zone", "zone_name", "zone_name");

cur_frm.add_fetch("event", "subject", "meeting_subject");
cur_frm.add_fetch("event", "starts_on", "from_date");
cur_frm.add_fetch("event", "ends_on", "to_date");
cur_frm.add_fetch("event", "cell", "cell");
cur_frm.add_fetch("event", "senior_cell", "senior_cell");
cur_frm.add_fetch("event", "pcf", "pcf");
cur_frm.add_fetch("event", "church", "church");
cur_frm.add_fetch("event", "church_group", "church_group");
cur_frm.add_fetch("event", "zone", "zone");
cur_frm.add_fetch("event", "region", "region");



frappe.ui.form.on("Attendance Record", "refresh", function(frm,dt,dn) {
    if(frm.doc.meeting_category=="Church Meeting"){
      hide_field('meeting_subject')
      unhide_field('meeting_sub')
    }
    else{
      unhide_field('meeting_subject')
      hide_field('meeting_sub')
    }
});

cur_frm.fields_dict['cell'].get_query = function(doc) {
  if (doc.church){
    return "select name,cell_code,cell_name from `tabCells` where church='"+doc.church+"'"
  }
  else{
    return "select name,cell_code,cell_name from `tabCells`"
  }
}

// frappe.ui.form.on("Attendance Record", "validate", function(frm,doc) {
   // if (frm.doc.meeting_category=="Cell Meeting"){
   //  if (!frm.doc.meeting_subject){
   //    msgprint(__("Please Enter Meeting Subject before save document.!"));
   //    throw "Enter Meeting Subject.!"
   //  }
   // }
   // if (frm.doc.meeting_category=="Church Meeting"){
   //  if (!frm.doc.meeting_sub){
   //    msgprint(__("Please Enter Meeting Subject before save document.!"));
   //    throw "Enter Meeting Subject.!"
   //  }
   // }

  //  if(frm.doc.from_date) {
  //   var date= frappe.datetime.now_datetime()
  //   if(frm.doc.from_date < date){
  //     msgprint(__("From Date should be todays or greater than todays date."));
  //     throw "Date should be proper.!"
  //   }
  // }
  // if(frm.doc.from_date) {
  //   if(frm.doc.from_date > frm.doc.to_date){
  //     frappe.msgprint(__("To Date should be greater than start date."));
  //     return;
  //     // msgprint(__("To Date should be greater than start date."));
  //     // throw "Date should be proper.!"
  //   }
  // }
// });

frappe.ui.form.on("Attendance Record", "meeting_category", function(frm,doc) {
  if (frm.doc.meeting_category=="Cell Meeting"){
    unhide_field('meeting_subject')
    hide_field('meeting_sub')
  }
  else if(frm.doc.meeting_category=="Church Meeting"){
    hide_field('meeting_subject')
    unhide_field('meeting_sub')
  }
});

// frappe.ui.form.on("Attendance Record", "from_date", function(frm,doc) {
//   if(frm.doc.from_date) {
//     var date= frappe.datetime.now_datetime()
//     if(frm.doc.from_date < date){
//       msgprint("From Date should be todays or greater than todays date.");
//     }
//   }
// });
// frappe.ui.form.on("Attendance Record", "to_date", function(frm,doc) {
//   if(frm.doc.from_date) {
//     if(frm.doc.from_date > frm.doc.to_date){
//       msgprint("To Date should be greater than start date.");
//     }
//   }
// });


frappe.ui.form.on("Attendance Record", "event", function(frm,doc) {
  cur_frm.add_fetch("event", "subject", "meeting_subject");
  cur_frm.add_fetch("event", "starts_on", "from_date");
  cur_frm.add_fetch("event", "ends_on", "to_date");
});

frappe.ui.form.on("Attendance Record", "onload", function(frm) {
  if (frm.doc.__islocal){
    hide_field('meeting_subject')
    unhide_field('meeting_sub')
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
      'doctype':'Cells',
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
      'doctype':'Senior Cells',
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
      'doctype':'PCFs',
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
      'doctype':'Churches',
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
      'doctype':'Group Churches',
      'zone' : doc.zone,
      'region' : doc.region
    }
  }
}

cur_frm.fields_dict['zone'].get_query = function(doc) {
  return {
    query:'church_ministry.church_ministry.doctype.member.member.get_list',
    filters :{
      'doctype':'Zones',
      'region' : doc.region
    }
  }
}