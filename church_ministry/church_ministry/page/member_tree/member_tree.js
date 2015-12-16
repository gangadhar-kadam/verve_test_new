// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// tree of chart of accounts / cost centers
// multiple companies
// add node
// edit node
// see ledger

frappe.pages["Member tree"].on_page_load  = function(wrapper){
	frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Member tree',
		single_column: true
	})
	var main = $(wrapper).find(".layout-main").html("<div class='user-settings'></div>\
	<table class='table table-condensed'>\
	<tr><td style='width:45%;'><div id= 'chart_area1'></div></td>\
	<td style='width:55%;'><div id= 'template_area'></div><div id= 'test_results_details'></div></td></tr>\
	</table>")

	chart_area = $("#chart_area1")
		.css({"margin-bottom": "15px", "min-height": "200px"})

	template_area = $("#template_area")

	var ctype = frappe.get_route()[1] || 'Account';
	var mail_to = {};

	wrapper.$from_date = wrapper.appframe.add_date('From Date');
	wrapper.$to_date = wrapper.appframe.add_date('To Date');

	wrapper.$company_select = wrapper.appframe.add_select("Purpose", ['','Mail', 'Ticker'])
		.change(function() {
			erpnext.account_chart = new erpnext.AccountsChart(ctype, $(this).val(),	chart_area.get(0), mail_to, wrapper.$from_date.val(), wrapper.$to_date.val());
			erpnext.template = new erpnext.Template(template_area.get(0), mail_to, $(this).val())
		})

	// erpnext.account_chart = new erpnext.AccountsChart(ctype, $(this).val(),	chart_area.get(0), mail_to);
	// erpnext.template = new erpnext.Template(template_area.get(0), mail_to)
}

erpnext.AccountsChart = Class.extend({
	init: function(ctype, purpose, wrapper, mail_to, from_date, to_date) {
		$(wrapper).empty();
		var me = this;
		me.ctype = ctype;
		me.purpose = purpose;
		this.tree = new frappe.ui.Tree({
			parent: $(wrapper),
			label: "Users",
			args: {'from_date': from_date, 'to_date': to_date},
			method: 'frappe.core.page.mail_ticker_manager.mail_ticker_manager.get_children',
			click: function(link) {
				// bold
				$('.bold').removeClass('bold'); // deselect
				$(link).parent().find('.balance-area:first').addClass('bold'); // select

			},
			toolbar: [
				{ toggle_btn: me.purpose == 'Mail'?true : false },
				{
					condition: function(node) { return !node.root },
					label: __("Add To Notifier List"),
					click: function(node) {
						console.log(node)
						if(!node.data.listed){
							me.set_span(node, mail_to)
						}
						else{
						 	var ids = node.data.value.replace(/[`~!@#$%^&*()_|+\-=?;:'" ,.<>\{\}\[\]\\\/]/gi, '_')
						 	console.log(ids)
						 	console.log($('#'+ids))
						 	$('#'+ids).removeClass('icon-check')
						 	$("#"+ids).remove()
						 	node.data.listed = null
						 	mail_to[node.parent_label].splice(mail_to[node.parent_label].indexOf(node.label), 1)
						}
					}
				}
			],
			onrender: function(node) {
				if(node.label!='Users'){
					me.set_span(node, mail_to)
				}
			}
		});
	},
	set_span :function(node, mail_to){
		if(!mail_to[node.parent_label]){
			mail_to[node.parent_label] = []
		}
		var ids = node.data.value.replace(/[`~!@#$%^&*()_|+\-=?;:'" ,.<>\{\}\[\]\\\/]/gi, '_');
		$('<span id = "'+ids+'" class="balance-area pull-right text-muted icon-check"></span>').insertBefore(node.$ul);
		node.data.listed = 1;
		mail_to[node.parent_label].push(node.label)
	}
});

erpnext.Template = Class.extend({
 	init: function(wrapper, mail_to, purpose) {
		this.wrapper = wrapper;
		this.mail_to = mail_to;
		this.render_fields(purpose);
	},
	render_fields: function(purpose){
		var me = this;
		$('#test_results_details').empty();

		if(purpose == 'Mail'){
			me.create_link('user_add','Templates','Email Template');
			this.create_fields({'fieldtype':'Text Editor', 'button_name':'Send Mail', 'purpose':purpose})
		}
		else if(purpose == 'Ticker'){
			 me.create_link('ticker','Ticker','Ticker Master');
			me.create_fields({'fieldtype':'Text', 'button_name':'Add Ticker', 'purpose':purpose})
		}
	},
	create_link: function(field_name, label, doctype_name){
		var me = this;
		this.tlink = frappe.ui.form.make_control({
				df: {
					"fieldtype": 'Link',
					"fieldname": field_name,
					"placeholder": label,
					"options": doctype_name
				},
				parent:$('#test_results_details'),
			});
		this.tlink.make_input();
		
		this.tlink.$input.on("change", function() {
			me.set_email_body(me.tlink.$input.val())
		});
	},
	create_fields: function(field_details){
		var me = this;
		this.cust_curr = frappe.ui.form.make_control({
				df: {
					"fieldtype": field_details['fieldtype'],
					"fieldname": "user_add",
					"placeholder":"Users"
				},
				parent:$('#test_results_details'),
			});
			this.cust_curr.make_input();

		$("<button class='btn btn-info'>"+__(field_details['button_name'])+"</button>")
			.appendTo($("<p>").appendTo($('#test_results_details')))
			.click(function(){
				me.manage_mail_ticker(field_details['purpose'])
			})
	},
	set_email_body: function(template_name){
		var me = this;
		frappe.call({
			method: 'frappe.core.page.mail_ticker_manager.mail_ticker_manager.get_email_body',
			args: {'template_name': template_name},
			callback: function(r){
				$(me.cust_curr.wrapper).find(".frappe-list").html(r.message)
			}
		})
	},
	manage_mail_ticker: function(purpose){
		var me = this;
		var message = '';
		if(purpose == 'Mail'){
			message = me.cust_curr.wrapper.innerText;
		}
		else if(purpose == 'Ticker'){
			message = me.cust_curr.$input.val()
		}
		frappe.call({
			method: 'frappe.core.page.mail_ticker_manager.mail_ticker_manager.manage_mail_ticker',
			args: {'recipient':me.mail_to, 'purpose': purpose, 'message': message},
			callback: function(r){
				frappe.msgprint("Done....")
			}
		})

	} 
})
