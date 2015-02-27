// set region and zone from church group and zone trigger
cur_frm.add_fetch("church_group", "region", "region");
cur_frm.add_fetch("church_group", "zone", "zone");
cur_frm.add_fetch("zone", "region", "region");

cur_frm.cscript.email_id = function(doc, dt, dn) {
   var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
   check=re.test(doc.email_id)
   if(check==false)
   {
        cur_frm.set_value("email_id", '')
        msgprint("Please Enter valid Email Id..! ");
        throw "Please Enter Correct Email ID.!"
   }
}