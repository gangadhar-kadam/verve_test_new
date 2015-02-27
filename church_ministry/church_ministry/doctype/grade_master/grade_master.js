cur_frm.cscript.to_score = function(doc, dt, dn) {
   if(doc.from_score){
   		if(doc.from_score>=doc.to_score){
   			msgprint("To-Score should be greater than From-Score..! ");
        	throw "Please Enter valid score!"
   		}
   }
}