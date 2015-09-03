frappe.pages['message-broadcast'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Broadcast Message',
		single_column: true
	});
	$("<div class='apllybtn' style='min-height: 20px;padding-left: 20px;padding-right: 20px;align:right;'  align='right'></div><div class='main_table' style='min-height: 20px;padding-left: 20px;padding-right: 20px;padding-bottom: 20px;'></div>").appendTo($(wrapper).find('.layout-main-section'));
	new frappe.assign(wrapper);
}

frappe.assign = Class.extend({
	init: function(wrapper) {
		this.wrapper = wrapper;
		this.body = $(this.wrapper).find(".main_table");
		this.make();
	},
	make: function() {
		var me = this; 
		h='<div class="sendsms" style="display:inline-block;width:50%;"></div><div class="add_contacts" style="display:inline-block;width:50%;"></div>';	               
		$(h).appendTo($(me.wrapper).find('.main_table'))
		me.setup_sms();
		me.add_contact();		  
	},
	setup_sms: function(){
		var me = this;
        $('<form>Message<textarea id="message" rows="4" cols="50"></textarea>&nbsp;&nbsp;<button class="btn btn-primary btn-send" id="send">Send SMS</button>&nbsp;&nbsp;<button class="btn btn-primary btn-send_email" id="send_email">Send Email</button></form>').appendTo($(me.wrapper).find('.sendsms'))
        $("<br><table class='contact_details' border='1' style='width:100%;background-color: #f9f9f9;'><tr><td style='padding=0px;width=50%''><b>&nbsp;Name</b></td><td><b>&nbsp;Number</b></td><td><b>&nbsp;Email ID</b></td></tr><tbody>").appendTo($(me.wrapper).find('.sendsms'))
        $('.sendsms').find('.btn-send').click(function() {         
				$('.btn-send').prop("disabled", false);
				var msg=$('#message').val();
				num_list=[]
				$(".contact_details tr").each(function(i,obj){
					if (i!=0){
						num_list.push($(obj).find('td:nth-child(2)').text())
					}				
				})
				frappe.call({
			        method:"church_ministry.church_ministry.page.message_broadcast.message_broadcast.send_sms1",
			        args:{
			        	"numbers":num_list,
			        	"msg":msg,
			        	"user":user
			        	},
			        callback: function(r) {
						console.log(r.message);	     				    
			        }                     
		        })  				
		})

		$('.sendsms').find('.btn-send_email').click(function() { 
				$('.btn-send_email').prop("disabled", false);
				var msg=$('#message').val();
				member_name=[]
				$(".contact_details tr").each(function(i,obj){
					if (i!=0){
						member_name.push($(obj).find('td:nth-child(3)').text())
					}				
				})
				
				frappe.call({
			        method:"church_ministry.church_ministry.page.message_broadcast.message_broadcast.user_send_mail",
			        args:{
			        	"member_name":member_name,
			        	"user":user,
			        	"msg":msg
			        	},
			        callback: function(r) {
						console.log(r.message);	     				    
			        }                     
		        })				
		})
	},
	add_contact: function(){
		var me = this;
        $('<form>Select Contact List: <select id="type"><option value="members">Members</option><option value="ftv">First Timers</option><option value="ic">Invitees and Contacts</option><option value="l">All Leaders</option></select><br><br>Select Gender &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <select id="gender"><option value=""></option><option value="male">Male</option><option value="Female">Female</option></select><br><br>Select Age Group : <select id="age"><option value=""></option><option value="a1">Youngster (20 to 25)</option><option value="a2">Young Adult (26 to 35)</option><option value="a3">Mid Age (35 to 45)</option><option value="a4">Arrived ( 45 to 55)</option><option value="a5">Seniors (56 to 65)</option><option value="a6">Advanced (65 and Above)</option></select><form>&nbsp;&nbsp;&nbsp;<br><br><button  class="btn btn-primary btn-search" onclick="add_cnt();"  id="search">Search</button>&nbsp;&nbsp;&nbsp;<button class="btn btn-primary btn-select" id="selectall">Select All</button>&nbsp;&nbsp;&nbsp;<button class="btn btn-primary btn-add" id="add">Add To List</button>').appendTo($(me.wrapper).find('.add_contacts'))
        $('.add_contacts').find('.btn-select').click(function() {         
				$('.btn-select').prop("disabled", false);
				$(':checkbox').each(function () {
					$(this).prop('checked', true);
	    		}) 
		})
		$('.add_contacts').find('.btn-add').click(function() {         
				$('.btn-add').prop("disabled", false); 
				$('.btn-send_email').prop("disabled", false);

				$('.members').find('tr').each(function () {
					var row = $(this);
					var $td = $('td', row);
					var flag = false;
					if ($td.find('input[type="checkbox"]').is(':checked')) {
						// $(this).find('td:nth-child(1),td:nth-child(5)').remove();
						var e_id = $(this).find('td:nth-child(4)').text();
						// var tbl = $(this).removeClass("members").addClass("member").appendTo($(me.wrapper).find('.sendsms')); 
						$('.contact_details').find('tr').each(function(i,j){
							if(i!=0){
								if(e_id==$(this).find('td:nth-child(3)').text()){
									flag = true;
								}
							}
						});
						if(!flag){
							$(this).find('td:nth-child(1),td:nth-child(5)').remove();
							$(this).appendTo($('.contact_details'));
						}
						else{
							msgprint("User '"+$(this).find('td:nth-child(2)').text()+"' already in list..")
						}
					}
				});
		})
		$('.add_contacts').find('.btn-search').click(function() {         
				$('.btn-search').prop("disabled", false); 
		})
	}
});

var add_cnt = function(){
	args={}
	if ($('#type :selected').text()){
		args['type'] = $('#type :selected').text()
	}
	if ($('#gender :selected').text()){
		args['sex'] = $('#gender :selected').text()
	}
	if ($('#age :selected').text()){
		args['age_group'] = $('#age :selected').text()
	}
	$('.members').remove();
	frappe.call({
	        method:"church_ministry.church_ministry.page.message_broadcast.message_broadcast.get_list",
	        args:{"arg":args},
	        callback: function(r) {
	            	h1=''		            
			            for (i=0;i<r.message.members.length;i++){
			                        var j=i+1
			                        h1 += '<tr >'
			                        h1 += '<td style="padding=0px;width=100%">&nbsp;'+j+'</td>'
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.members[i][0]+'</td>'
			                        h1 += '<td style="padding=0px;width=100%">'+r.message.members[i][1]+'</td>'
			                        h1 += '<td style="padding=0px;width=100%"><a href="desk#Form/User/'+r.message.members[i][2]+'">&nbsp;'+r.message.members[i][2]+'</a></td>'                  
			                        h1 += "<td style='padding=0px;width=100%'>&nbsp;<input type='checkbox' data-name='"+r.message.members[i][0]+"' ></td></tr>"
			            }  
			            h="<table class='members' border='1' style='width:100%;background-color: #f9f9f9;'><tr><td style='padding=0px;width=100%''><b>&nbsp;Sr No.</b></td><td><b>&nbsp;Name</b></td><td><b>&nbsp;Number</b></td><td><b>&nbsp;Email ID</b></td><td><b>&nbsp;Invite</b></td></tr>"+h1+"<tbody>";	               
			            $(h).appendTo($('.add_contacts'))					    
	        }                     
        })     
 }

 var select_all = function(){
	
 }



