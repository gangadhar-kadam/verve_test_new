cur_frm.add_fetch("member", "member_name", "member_name");
cur_frm.add_fetch("ftv", "ftv_name", "ftv_name");

cur_frm.add_fetch("member", "cell", "cell");
cur_frm.add_fetch("member", "senior_cell", "senior_cell");
cur_frm.add_fetch("member", "pcf", "pcf");
cur_frm.add_fetch("member", "church", "church");
cur_frm.add_fetch("member", "church_group", "church_group");
cur_frm.add_fetch("member", "zone", "zone");
cur_frm.add_fetch("member", "region", "region");

cur_frm.add_fetch("ftv", "ftv_owner", "member1");
cur_frm.add_fetch("ftv", "cell", "cell");
cur_frm.add_fetch("ftv", "senior_cell", "senior_cell");
cur_frm.add_fetch("ftv", "pcf", "pcf");
cur_frm.add_fetch("ftv", "church", "church");
cur_frm.add_fetch("ftv", "church_group", "church_group");
cur_frm.add_fetch("ftv", "zone", "zone");
cur_frm.add_fetch("ftv", "region", "region");

frappe.ui.form.on("Partnership Arm Record", "validate", function(frm,doc) {
	if(frm.doc.is_member==1){
		console.log("1")
		if(!frm.doc.member){
			console.log("11")
			msgprint("Please select Member for Partnership Arm Record before save..! ");
        	throw "Please select Member!"
		}
	}
	else if(frm.doc.is_member==0){
		if(!frm.doc.ftv){
			msgprint("Please select FTV for Partnership Arm Record before save..! ");
        	throw "Please select FTV!"
		}
	}
});

frappe.ui.form.on("Partnership Arm Record", "member", function(frm,doc) {
	if(!frm.doc.member){
		frm.doc.member_name=" ";
		refresh_field("member_name");
	}
});

frappe.ui.form.on("Partnership Arm Record", "ftv", function(frm,doc) {
	if(!frm.doc.ftv){
		frm.doc.ftv_name=" ";
		refresh_field("ftv_name");
	}
});