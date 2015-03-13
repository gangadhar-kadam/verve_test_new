
frappe.ui.form.on("Grade Master", "to_score", function(frm,doc) {
    if(frm.doc.from_score){
   		if(frm.doc.from_score>=frm.doc.to_score){
   			msgprint("To-Score should be greater than From-Score..! ");
        	throw "Please Enter valid score!"
   		}
   }
});