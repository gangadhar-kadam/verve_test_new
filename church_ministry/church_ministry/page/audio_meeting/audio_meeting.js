frappe.pages['audio-meeting'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'None',
		single_column: true
	});
	$("<br><div class='main_table' style='min-height: 20px;padding-left: 20px;padding-right: 20px;padding-bottom: 20px;'></div>").appendTo($(wrapper).find('.layout-main-section'));
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
		h='<div class="add_contacts" style="display:inline-block;width:58%;"></div><div style="display:inline-block;width:2%;">&nbsp;&nbsp;</div><div class="sendsms" style="display:inline-block;width:40%;"></div>';	               
		$(h).appendTo($(me.wrapper).find('.main_table'))
		me.setup_sms();
		me.add_contact();		  
	},
	setup_sms: function(){
		var me = this;
        $('<form><button class="btn btn-primary btn-send" id="send">Invite for Meeting</button></form>').appendTo($(me.wrapper).find('.sendsms'))
        $("<br><table class='contact_details' border='1' style='width:100%;background-color: #f9f9f9;'><tr><td style='padding=0px;width=50%''><b>&nbsp;Full Name</b></td><td><b>&nbsp;Email ID</b></td></tr><tbody>").appendTo($(me.wrapper).find('.sendsms'))
        $('.btn-send').prop("disabled", true);
        $('.add_contacts').find('.btn-add').prop("disabled", true);
        $('.sendsms').find('.btn-send').click(function() {         
				$('.btn-send').prop("disabled", true);
				$('.add_contacts').find('.btn-add').prop("disabled", true);
				var name=[]
				var full_name=[];
				$(".contact_details tr").each(function(i,obj){
					if (i!=0){
						   name.push($(obj).find('td:nth-child(2)').text().replace(' ',''));
						   full_name.push($(obj).find('td:nth-child(1)').text());
					}				
				})
				frappe.call({
			        method:"church_ministry.church_ministry.page.audio_meeting.audio_meeting.process",
			        args:{
			        	"data":name		        	
			        	},
			        callback: function(r) {
			        	//window.location.reload();
						    				    
			        }                     
		        })  

	})		

	},
	add_contact: function(){
		var me = this;
        $('<form>Hello&nbsp;&nbsp;'+user+',&nbsp;&nbsp;Please select the users for Meeting..!&nbsp;&nbsp;&nbsp;&nbsp;<button class="btn btn-primary btn-add" id="add">Add participants to list</button><br></form>').appendTo($(me.wrapper).find('.add_contacts'))
        add_cnt();
        $('.add_contacts').find('.btn-select').click(function() {         
				$('.btn-select').prop("disabled", false);				
				$(':checkbox').each(function () {
					$(this).prop('checked', true);
					$('.add_contacts').find('.btn-add').prop("disabled", false);
	    		}) 
		})
		$('.add_contacts').find('.btn-add').click(function() {         
				$('.btn-add').prop("disabled", false); 
                $('.btn-send').prop("disabled", false);
				$('.members').find('tr').each(function () {
					var row = $(this);
					var $td = $('td', row);					
					if ($td.find('input[type="checkbox"]').is(':checked')) {						
						$(this).find('td:nth-child(1),td:nth-child(4)').remove();
						var tbl = $(this).removeClass("members").addClass("member").appendTo($(me.wrapper).find('.sendsms')); 
						$(tbl).appendTo($('.contact_details'));
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
	$('.members').remove();
	frappe.call({
				method:"church_ministry.church_ministry.page.audio_meeting.audio_meeting.get_users",
				callback: function(r) {									
								h1=''		            
		            			for (i=0;i<r.message.length;i++){						         
		                        var j=i+1
		                        h1 += '<tr >'
		                        h1 += '<td style="padding=0px;width=100%">&nbsp;'+j+'</td>'		                  
		                        h1 += '<td style="padding=0px;width=100%">'+r.message[i]['full_name']+'</td>' 
		                        h1 += '<td style="padding=0px;width=100%"><a href="desk#Form/User/'+r.message[i]['name']+'">&nbsp;'+r.message[i]['name']+'</a></td>'                  
		                        h1 += "<td style='padding=0px;width=100%'>&nbsp;<input type='checkbox' data-name='"+r.message[i]['name']+"' ></td></tr>"
		            }
		            h="<br><table class='members' border='1' style='width:100%;background-color: #f9f9f9;'><thead><tr><td style='padding=0px;width=100%'><b>&nbsp;Sr No.</b></td><td style='padding=0px;width=40%'><b>&nbsp;Full Name</b></td><td style='padding=0px;width=40%'><b>&nbsp;Email ID</b></td><td><b>&nbsp;Select</b></td></tr></thead><tbody style='max-height: 100px; overflow: hidden'>"+h1+"</tbody>";
		            $(h).appendTo($('.add_contacts'))	
			 	}	
	    });    
 }
