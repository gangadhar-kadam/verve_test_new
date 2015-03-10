frappe.pages['approve-ftv-to-membe'].on_page_load = function(wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Eligible FT List  for Membership',
		single_column: true
	});
	$("<div class='apllybtn' style='min-height: 20px;padding-left: 20px;padding-right: 20px;align:right;'  align='right'></div><div class='assignt' style='min-height: 20px;padding-left: 20px;padding-right: 20px;padding-bottom: 20px;'></div>").appendTo($(wrapper).find('.layout-main-section'));
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
			callback: function(r) {
				me.options = r.message;
				me.setup_page();
			}
		});		  
	},
	setup_page: function(){
		var me = this;
		$(me.wrapper).find('.assignt').empty();
		frappe.call({
				method:"church_ministry.church_ministry.page.approve_ftv_to_membe.approve_ftv_to_membe.loadftv",
				args:{
	        	},
				callback: function(r) {
					if (r.message.ftv){
						//console.log(r.message);
						h1=''		            
			            for (i=0;i<r.message.ftv[0].length;i++){
			                        var j=i+1
			                        h1 += '<tr >'
			                        h1 += '<td style="padding=0px;width=100%">'+j+'</td>'
			                        h1 += '<td style="padding=0px;width=100%"><a href="desk#Form/First Time Visitor/'+r.message.ftv[0][i][0]+'">'+r.message.ftv[0][i][0]+'</a></td>'
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.ftv[0][i][1]+'</td>'
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.ftv[0][i][2]+'</td>'
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.ftv[0][i][3]+'</td>'                      
			                        h1 += "<td style='padding=0px;width=100%'><input type='checkbox' data-name='"+r.message.ftv[0][i][0]+"' ></td></tr>"
			            }
			            $('<br><button  class="btn btn-primary btn-search" id="test">Approve</button><br>').appendTo($(me.wrapper).find('.apllybtn'));    
			            h="<br><table class='members1' border='1' style='width:100%;background-color: #f9f9f9;'><tr><td style='padding=0px;width=100%''><b>Sr No.</b></td><td><b>FT ID</b></td><td><b>FT Name</b></td><td><b>Gender</b></td><td><b>DOB</b></td><td><b>Approve</b></td></tr>"+h1+"<tbody>";	               
			            $(h).appendTo($(me.wrapper).find('.assignt'))
					    $('.apllybtn').find('.btn-search').click(function() {
					    	var ftv =[];
							$("input[type='checkbox']").each(function () {
											if ($(this).prop("checked")==true) { 
												ftv[ftv.length]=$(this).attr('data-name');
											}
							})/
						    assign(ftv);                      
						}) ;
					}
			 	}                
	    });	
	}	
});

var assign = function(ftv){
	frappe.call({
	        method:"church_ministry.church_ministry.page.approve_ftv_to_membe.approve_ftv_to_membe.approveftv",
	        args:{
	        	"ftv":ftv      
	        },        
	        callback: function(r) {
	            if (r.message=='Done'){
	                alert("The First Timer Visitors are successfully approved for member conversion ..!");
	                location.reload();
	            }
	            else{
	                alert("Invalid Assignment ");
	            }
	        }                     
        })  
 }