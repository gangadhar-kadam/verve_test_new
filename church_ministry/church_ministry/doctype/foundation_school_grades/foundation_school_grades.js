
frappe.ui.form.on("Foundation School Grades", "validate", function(frm,doc) {
   if(frm.doc.from_score && frm.doc.to_score){
   		if(parseInt(frm.doc.from_score)>=parseInt(frm.doc.to_score)){
   			msgprint("From-Score should be less than To-Score..! ");
        validated = 0;
   		}
   }
});
