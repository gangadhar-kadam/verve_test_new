//cur_frm.add_fetch("church", "church_group", "church_group");
cur_frm.add_fetch("church", "region", "region");
cur_frm.add_fetch("church", "zone", "zone");
cur_frm.add_fetch("church", "church_name", "church_name");

frappe.ui.form.on("Foundation School Exam", "onload", function(frm,cdt,cdn,doc) {
	if(frm.doc.__islocal){
    cur_frm.fields_dict["attendance"].grid.set_column_disp("attendance",false );
  	}
  	cur_frm.cscript.toggle_related_fields(frm.doc);
});

frappe.ui.form.on("Foundation School Exam", "refresh", function(frm,cdt,cdn,doc) {
    cur_frm.fields_dict["attendance"].grid.set_column_disp("attendance",true );
    cur_frm.cscript.toggle_related_fields(frm.doc);
});

cur_frm.cscript.score = function(doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.call({
				method:"church_ministry.church_ministry.doctype.foundation_school_exam.foundation_school_exam.get_grade",
				args:{
	        	"score" : d.score
	        	},
				callback: function(r) {
					if (r.message){
						d.grade=r.message.grade;
			           cur_frm.refresh_fields();
			        }
			 }
	    })
}

frappe.ui.form.on("Foundation School Exam", "church", function(frm,cdt,cdn,doc) {
		var d = locals[cdt][cdn];
		frappe.call({
				method:"church_ministry.church_ministry.doctype.foundation_school_exam.foundation_school_exam.loadftv",
				args:{
	        	"church":frm.doc.church,
	        	"visitor_type":frm.doc.visitor_type
	        	},
				callback: function(r) {
					console.log(['result ',r.message.ftv[0]]);
					if (r.message.ftv[0].length>0){
					   frappe.model.clear_table(frm.doc, "attendance");
					   cur_frm.refresh_fields();
			           for (i=0;i<r.message.ftv[0].length;i++){
			           	    var child = frappe.model.add_child(frm.doc,"Foundation School Exam Details","attendance");
			           	    if (frm.doc.visitor_type=='FTV'){
			           	    	child.ftv_id=r.message.ftv[0][i][0];
			           	    }
			           	    else{
			           	    	child.member_id=r.message.ftv[0][i][0];
			           	    }
			           	    child.ftv_name=r.message.ftv[0][i][1];
			           	    child.cell=r.message.ftv[0][i][2];
			           }
			           cur_frm.refresh_fields();
			        }
			 }
	    })
});

frappe.ui.form.on("Foundation School Exam", "visitor_type", function(frm,doc) {
	frappe.model.clear_table(frm.doc, "attendance");
	cur_frm.cscript.toggle_related_fields(frm.doc);
});

cur_frm.cscript.toggle_related_fields = function(doc) {
	if (doc.visitor_type=='FTV'){
		cur_frm.fields_dict["attendance"].grid.set_column_disp("member_id",false );
		cur_frm.fields_dict["attendance"].grid.set_column_disp("ftv_id", true);
		cur_frm.refresh_fields();
	}
	else {
		cur_frm.fields_dict["attendance"].grid.set_column_disp("member_id",true );
		cur_frm.fields_dict["attendance"].grid.set_column_disp("ftv_id", false);
		cur_frm.refresh_fields();
	}
}

cur_frm.add_fetch("foundation__exam", "max_score", "max_score");
cur_frm.add_fetch("foundation__exam", "min_score", "min_score");
cur_frm.add_fetch("ftv_id", "ftv_name", "ftv_name");

