# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, validate_email_add, cint
from frappe import throw, _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe import msgprint, _

class FirstTimeVisitor(Document):
	
	def validate(self):
		if self.date_of_birth and self.date_of_visit and getdate(self.date_of_birth) >= getdate(self.date_of_visit):		
			frappe.throw(_("Date of Visit '{0}' must be greater than Date of Birth '{1}'").format(self.date_of_visit, self.date_of_birth))
		if self.baptisum_status=='Yes':
			if not self.when or self.where :
				frappe.throw(_("When and Where is Mandatory if 'Baptisum Status' is 'Yes'..!"))

	def on_update(self):
		usr_id=frappe.db.sql("select name from `tabUser` where name='%s'"%(self.email_id),as_list=1)
		# u_rle=frappe.db.sql("select parent from `tabUserRole` where role='First Time Visitor'")
		if self.flag=='not':
			if usr_id:
				msgprint(_("User is already created for respective email_id.."), raise_exception=1)
			else:
				frappe.errprint("user")
				usr = frappe.new_doc("User")
				usr.email=self.email_id
				usr.first_name = self.ftv_name
				usr.new_password = 'password'
				usr.insert() 
				frappe.errprint("role")
				rle=frappe.new_doc("UserRole")
				rle.parent=self.email_id
				rle.parentfield='user_roles'
				rle.parenttype='User'
				rle.role='First Time Visitor'
				rle.insert()

				value = frappe.new_doc("DefaultValue")
				value.parentfield = 'system_defaults'
				value.parenttype = 'User Permission'
				value.parent = self.email_id
				value.defkey = 'First Time Visitor'
				value.defvalue = self.name
				value.insert()
			frappe.db.sql("update `tabFirst Time Visitor` set flag='SetPerm' where name='%s'"%(self.name))
			frappe.db.commit()

	# def get_related_fields(self):
		

@frappe.whitelist()
def make_member(source_name, target_doc=None):
	return _make_member(source_name, target_doc)

def _make_member(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		pass

	doclist = get_mapped_doc("First Time Visitor", source_name,
		{"First Time Visitor": {
			"doctype": "Member",
			"field_map": {				
				"name":"ftv_id_no",
				"ftv_name":"member_name"
			}
		}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	return doclist

def validate_birth(doc,method):
		if doc.date_of_birth and doc.date_of_visit and getdate(doc.date_of_birth) >= getdate(doc.date_of_visit):		
			frappe.throw(_("Date of Visit '{0}' must be greater than Date of Birth '{1}'").format(doc.date_of_visit, doc.date_of_birth))
		if doc.baptisum_status=='Yes':
			if not doc.when or doc.where :
				frappe.throw(_("When and Where is Mandatory if 'Baptisum Status' is 'Yes'..!"))

@frappe.whitelist()
def ismember(name):
	converted=frappe.db.sql("select name from `tabMember` where ftv_id_no='%s'"%(name))
	if converted:
		return "Yes"
	else:
		return "No"