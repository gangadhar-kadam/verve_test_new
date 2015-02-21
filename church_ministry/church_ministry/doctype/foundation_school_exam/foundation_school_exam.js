
$.extend(cur_frm.cscript, {
  onload:function (doc,dt,dn){  
       cur_frm.cscript.toggle_related_fields(doc);
  },
  refresh: function (doc, dt, dn) {
		cur_frm.cscript.toggle_related_fields(doc);
	},
});

cur_frm.cscript.score = function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	return get_server_fields('get_grade', d.score, '', doc, cdt, cdn, 1);
}

frappe.ui.form.on("Foundation School Exam", "cell", function(frm,cdt,cdn,doc) {
		var d = locals[cdt][cdn];
		frappe.call({
				method:"church_ministry.church_ministry.doctype.foundation_school_exam.foundation_school_exam.loadftv",
				args:{
	        	"cell":frm.doc.cell,
	        	"visitor_type":frm.doc.visitor_type
	        	},
				callback: function(r) {
					if (r.message.ftv[0].length>0){
						frappe.model.clear_table(frm.doc, "attendance");
			           for (i=0;i<r.message.ftv[0].length;i++){
			           	    var child = frappe.model.add_child(frm.doc,"Foundation School Exam Details","attendance");
			           	    if (frm.doc.visitor_type=='FTV'){
			           	    	child.ftv_id=r.message.ftv[0][i][0];
			           	    }
			           	    else{
			           	    	child.member_id=r.message.ftv[0][i][0];
			           	    }
			           	    child.ftv_name=r.message.ftv[0][i][1];
			           } 
			           refresh_field("attendance");
			        }
			 }
	    })
});

frappe.ui.form.on("Foundation School Exam", "visitor_type", function(frm,doc) {
	frappe.model.clear_table(frm.doc, "attendance");
	cur_frm.cscript.toggle_related_fields(frm.doc);
	//frappe.model.clear_table(doc, "attendance");

});


cur_frm.cscript.toggle_related_fields = function(doc) {
	if (doc.visitor_type=='FTV'){
		cur_frm.fields_dict["attendance"].grid.set_column_disp("member_id",false );
		cur_frm.fields_dict["attendance"].grid.set_column_disp("ftv_id", true);
	}
	else {
		cur_frm.fields_dict["attendance"].grid.set_column_disp("member_id",true );
		cur_frm.fields_dict["attendance"].grid.set_column_disp("ftv_id", false);
	}
}

cur_frm.add_fetch("foundation__exam", "max_score", "max_score");
cur_frm.add_fetch("foundation__exam", "min_score", "min_score");
cur_frm.add_fetch("ftv_id", "ftv_name", "ftv_name");

