// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.pages["member-tree"].on_page_load = function(wrapper){
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		single_column: true,
	});

	frappe.breadcrumbs.add("Church Ministry")

	wrapper.page.set_secondary_action(__('Refresh'), function() {
			wrapper.make_tree();
		});

	wrapper.make_tree = function() {
		var ctype = frappe.get_route()[1] || 'Regions';
		return frappe.call({
			method: 'church_ministry.church_ministry.page.member_tree.member_tree.get_children',
			args: {ctype: ctype},
			callback: function(r) {
				var root = "Member Tree";
				erpnext.church_chart = new erpnext.ChurchChart(ctype, root, page,
					page.main.css({
						"min-height": "300px",
						"padding-bottom": "25px"
					}));
			}
		});
	}

	wrapper.make_tree();
}

frappe.pages['member-tree'].on_page_show = function(wrapper){
	// set route
	var ctype = frappe.get_route()[1] || 'Regions';

	wrapper.page.set_title(__('Hierarchy Tree'));

	wrapper.make_tree();
};

erpnext.ChurchChart = Class.extend({
	init: function(ctype, root, page, parent) {
		$(parent).empty();
		var me = this;
		me.ctype = 'Regions';
		me.page = page;
		me.can_read = frappe.model.can_read(this.ctype);
		me.can_create = frappe.boot.user.can_create.indexOf(this.ctype) !== -1 ||
					frappe.boot.user.in_create.indexOf(this.ctype) !== -1;
		this.tree = new frappe.ui.Tree({
			parent: $(parent),
			label: __(root),
			args: {ctype: ctype},
			method: 'church_ministry.church_ministry.page.member_tree.member_tree.get_children',
			toolbar: [
				{toggle_btn: true},
				{
					label:__("Edit"),
					condition: function(node) {
						return !node.root && me.can_read;
					},
					click: function(node) {
						frappe.set_route("Form", node.label.split(':-')[0], node.label.split(':-')[1]);
					},

				},
				{
					label:__("Add Child"),
					condition: function(node) { return me.can_create && node.expandable; },
					click: function(node) {
						frappe.set_route("Form", node.label.split(':-')[0], "New "+node.label.split(':-')[0]);
					}
				}

			]
		});
	}

});
