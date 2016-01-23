// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

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

frappe.ui.form.on("Invitees and Contacts", "invited_by", function(frm,cdt, cdn) {
frappe.call({
        method:"church_ministry.church_ministry.page.convert_invitees_and.convert_invitees_and.loadmemberdetails",
        args:{
           "invited_by":frm.doc.invited_by
            },
        callback: function(r) {
          if (r.message){
            frm.doc.cell=r.message[0][0];
            frm.doc.senior_cell=r.message[0][1];
            frm.doc.pcf=r.message[0][2];
            frm.doc.church=r.message[0][3];
            frm.doc.church_group=r.message[0][4];
            frm.doc.zone=r.message[0][5];
            frm.doc.region=r.message[0][6];
            refresh_field('region');
            refresh_field('zone');
            refresh_field('church_group');
            refresh_field('church');
            refresh_field('pcf');
            refresh_field('senior_cell');
            refresh_field('cell'); 
          }
        }                
      }); 

});



frappe.ui.form.on("Invitees and Contacts", "onload", function(frm,cdt, cdn) {
  if(!frm.doc.__islocal){
    set_field_permlevel('email_id',1);
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
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',1);
    set_field_permlevel('church',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('pcf',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "PCF Leader")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',1);
    set_field_permlevel('church',2);
    set_field_permlevel('church_group',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Church Pastor")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',1);
    set_field_permlevel('church_group',2);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Group Church Pastor")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',1);
    set_field_permlevel('zone',2);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Zonal Pastor")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',0);
    set_field_permlevel('zone',1);
    set_field_permlevel('region',2);
  }
  else if(in_list(user_roles, "Regional Pastor")){
    set_field_permlevel('cell',0);
    set_field_permlevel('senior_cell',0);
    set_field_permlevel('pcf',0);
    set_field_permlevel('church',0);
    set_field_permlevel('church_group',0);
    set_field_permlevel('zone',0);
    set_field_permlevel('region',1);
  }  
});

/*frappe.ui.form.on("Invitees and Contacts", "refresh", function(frm,doc,dt,dn) {
    if(!frm.doc.__islocal ) {
      frm.add_custom_button(__("Create FT"), cur_frm.cscript.create_member,frappe.boot.doctype_icons["Customer"], "btn-default");     
    }
    
});

frappe.ui.form.on("Invitees and Contacts", "create_member", function(frm,doc) {
  console.log("hi buttom clicked");
    frappe.model.open_mapped_doc({
      method: "church_ministry.church_ministry.doctype.invitees_and_contacts.invitees_and_contacts.make_member",
      frm: cur_frm
    })
});*/

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

cur_frm.add_fetch("church", "church_group", "church_group");
cur_frm.add_fetch("church", "region", "region");
cur_frm.add_fetch("church", "zone", "zone");

cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");

cur_frm.add_fetch("zone", "region", "region");