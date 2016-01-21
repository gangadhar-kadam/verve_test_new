# Copyright (c) 2015, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, validate_email_add, cint
from frappe import throw, _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe import msgprint, _

class InviteesandContacts(Document):
	
	def validate(self):
		pass
		# if self.date_of_birth and self.date_of_visit and getdate(self.date_of_birth) >= getdate(self.date_of_visit):		
		# 	frappe.throw(_("Date of Visit '{0}' must be greater than Date of Birth '{1}'").format(self.date_of_visit, self.date_of_birth))
		# if self.baptisum_status=='Yes':
		# 	if not self.baptism_when or self.baptism_where :
		# 		frappe.throw(_("When and Where is Mandatory if 'Baptisum Status' is 'Yes'..!"))


@frappe.whitelist()
def make_member(source_name, target_doc=None):
	frappe.errprint("make member")
	return _make_member(source_name, target_doc)

def _make_member(source_name, target_doc=None, ignore_permissions=False):
	frappe.errprint("make member 2")
	def set_missing_values(source, target):
		pass
	frappe.errprint("make member 3")
	doclist = get_mapped_doc("Invitees and Contacts", source_name,
		{"Invitees and Contacts": {
			"doctype": "First Timer",
			"field_map": {				
				"invitee_contact_name": "ftv_name",
				"title":"address_manual",
				"designation":"designation"
			}
		}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	return doclist
