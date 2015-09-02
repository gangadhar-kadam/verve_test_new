frappe.pages['assign-for-followup'].on_page_load = function(wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Assign For Followup',
		single_column: true
	});
	$("<div class='assignt' style='min-height: 20px;padding-left: 20px;'><table class='table' style='width:100%; border-right: 1px solid;padding-left: 20px;' >First Timer Details<tr>\
	<td ><div id ='ftvi' style='min-height: 10px;padding-left: 20px;width:20%;display: inline-block;'></div><div id ='dtl' style='min-height: 10px;padding-top: 20px;padding-left: 20px;width:60%;display: inline-block;'></div><div id ='apllybtn' style='min-height: 10px;padding-top: 10px;padding-left: 20px;width:10%;display: inline-block;'></div></td>\
	</tr></table></div>").appendTo($(wrapper).find('.layout-main-section'));
	$("<div class='assignr' style='min-height: 400px; padding: 15px;'></div>").appendTo($(wrapper).find('.layout-main-section'));
	new frappe.assign(wrapper);
}	

frappe.assign = Class.extend({
	init: function(wrapper) {
		this.wrapper = wrapper;
		this.body = $(this.wrapper).find(".assignt");
		this.make();
	},
	make: function() {
		var me = this;
		return frappe.call({
			module:"church_ministry.church_ministry",
			page:"assign_for_followup",
			method: "ftv",
			// args:{
	  //       	"get_ftv_member": get_ftv_member       
	  //       	},
			callback: function(r) {
				me.options = r.message;
				me.setup_page();
			}
		});
		  
	},
	setup_page: function() {
		var me = this;
		this.ftv=frappe.ui.form.make_control({
		df: {
		    "fieldtype": "Link",
			"options": "First Timer",
			"label": "First Timer",
			"fieldname": "ftv",
			"placeholder": "FT Details (ID)"
			},
		"only_input":true,
		parent:$(me.wrapper).find("#ftvi"),
		});
		this.ftv.get_query = function() { 
			return{
					query: "church_ministry.church_ministry.page.assign_for_followup.assign_for_followup.loadftv"
				}
		}
		this.ftv.make_input();
		this.ftv.$input.on("change", function() {
			var ftv=me.ftv.$input.val();
			me.show_members(ftv)
		});
	},
	show_members: function(ftv){
		var me = this;
		$(me.wrapper).find('.assignr').empty();
		frappe.call({
				method:"church_ministry.church_ministry.page.assign_for_followup.assign_for_followup.loadmembers",
				args:{
	        	"ftv":ftv       
	        	},
				callback: function(r) {
					if (r.message.members){
			            h1="<table class='members1' border='1' style='width:100%;background-color: #f9f9f9;'> <b>Member Details</b><tr><td><b>Sr No.</b></td><td><b>Member ID</b></td><td><b>Member Name</b></td><td><b>Gender</b></td><td><b>Age Group</b></td><td><b>Distance</b></td><td><b>Assign Member</b></td></tr>"
			            for (i=0;i<r.message.members[0].length;i++){
			                    	//console.log(r.message.members[0][i][0]);
			                        var j=i+1
			                        h1 += '<tr >'
			                        h1 += '<td style="padding=0px;width=100%">'+j+'</td>'
			                        h1 += '<td style="padding=0px;width=100%"><a href="desk#Form/Member/'+r.message.members[0][i][0]+'">'+r.message.members[0][i][0]+'</a></td>'
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.members[0][i][1]+'</td>'
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.members[0][i][2]+'</td>'                      
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.members[0][i][3]+'</td>'
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.members[0][i][4]+'</td>'
			                        h1 += "<td style='padding=0px;width=100%'><input type='checkbox' name='"+r.message.members[0][i][0]+"' onclick=check_box('"+r.message.members[0][i][0]+"','"+ftv+"') ></td></tr></tbody>"
			            }  
			            $(h1).appendTo($(me.wrapper).find('.assignr'))        
					}
			 	}
	    });
		$("#dtl").empty();
		frappe.call({
				method:"church_ministry.church_ministry.page.assign_for_followup.assign_for_followup.ftvdetails",
				args:{
	        	"ftv":ftv       
	        	},
				callback: function(r) {
					if (r.message.ftv){
						dtl="<b>Name:</b>&nbsp;"+r.message.ftv[0][0][0]+" &nbsp; &nbsp;<b> Gender:</b>&nbsp;"+r.message.ftv[0][0][1]+" &nbsp; &nbsp;<b>Age Group:</b>&nbsp;"+r.message.ftv[0][0][4]+"&nbsp; &nbsp; <b>Address:</b>&nbsp;"+r.message.ftv[0][0][3]
			             $( "#dtl" ).append(dtl);      
					}
			 	}
	    }); 
		
	}  
});


var check_box = function(memberid,ftv){
	if ($("input[type='checkbox'][name='"+memberid+"']").prop("checked")==true) { 
		$(':checkbox').each(function () {
				$(this).removeAttr('checked');
	    })  
	    $("#apllybtn").empty();
	    $("input[type='checkbox'][name='"+memberid+"']").prop('checked', true);
	    $("#apllybtn").append('<button  class="btn btn-primary btn-search">&nbsp;&nbsp;&nbsp; Assign For Follow up</button>');
		$('#apllybtn').find('.btn-search').click(function() {         
				$('.btn-search').prop("disabled", true);
				$(':checkbox').each(function () {
					$(this).attr("disabled", true);
	    		}) 
        		assign(memberid,ftv);                      
		})
    }
    else{
    	$("#apllybtn").empty();
    }
 }


var assign = function(memberid,ftv){
	frappe.call({
	        method:"church_ministry.church_ministry.page.assign_for_followup.assign_for_followup.assignmember",
	        args:{
	        	"ftv":ftv,
	            "memberid":memberid        
	        },        
	        callback: function(r) {
	            if (r.message=='Done'){
	                alert("The Member '"+memberid+"' is successfully assigned to First Timer '"+ftv+"'");
	                location.reload();
	            }
	            else{
	                alert("Invalid Assignment ");
	            }
	        }                     
        })  
 }

  



