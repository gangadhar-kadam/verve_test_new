cur_frm.add_fetch("member", "member_name", "member_name");
cur_frm.add_fetch("ftv", "ftv_name", "ftv_name");

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