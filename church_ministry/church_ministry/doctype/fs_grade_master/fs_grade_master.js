
frappe.ui.form.on("FS Grade Master", "validate", function(frm,doc) {
    if(frm.doc.from_score){
   		if(frm.doc.from_score>=frm.doc.to_score){
   			msgprint("To-Score should be greater than From-Score..! ");
        	throw "Please Enter valid score!"
   		}
   }
   if(frm.doc.to_score){
   		if(frm.doc.from_score<=frm.doc.to_score){
   			msgprint("From-Score should be less than To-Score..! ");
        	throw "Please Enter valid score!"
   		}
   }
});
