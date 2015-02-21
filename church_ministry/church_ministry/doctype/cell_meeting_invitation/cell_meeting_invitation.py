# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class CellMeetingInvitation(Document):
	
	def  load_table(self):
		self.set('invitation_member_details', [])
		if self.cell:
			member_ftv = frappe.db.sql("select name,ftv_name,email_id from `tabFirst Time Visitor` where cell='%s' union select name,member_name,email_id from `tabMember` where cell='%s' "%(self.cell,self.cell))
		elif self.church:
			member_ftv = frappe.db.sql("select name,ftv_name,email_id from `tabFirst Time Visitor` where church='%s' union select name,member_name,email_id from `tabMember` where church='%s'"%(self.church,self.church))
		for d in member_ftv:
			child = self.append('invitation_member_details', {})
			child.member = d[0]
			child.member_name = d[1]
			child.email_id = d[2]


@frappe.whitelist()
def create_attendance(source_name, target_doc=None):
	def postprocess(source, doc):
		pass

	doc = get_mapped_doc("Cell Meeting Invitation", source_name, {
		"Cell Meeting Invitation": {
			"doctype": "Cell Meeting Attendance",
			# "validation": {
			# 	"docstatus": ["=", 1]
			# }
		},
		"Invitation Member Details": {
			"doctype": "Invitation Member Details",
			"field_map": {
				# "parent": "sales_order_no",
				# "stock_uom": "uom"
			}
		}
	}, target_doc, postprocess)

	return doc

@frappe.whitelist()
def create_event_attendance(source_name, target_doc=None):
	def postprocess(source, doc):
		pass

	doc = get_mapped_doc("Event", source_name, {
		"Event": {
			"doctype": "Event Attendance",
			# "validation": {
			# 	"docstatus": ["=", 1]
			# }
		},
		"Event Attendace Details": {
			"doctype": "Event Attendace Details",
			"field_map": {
				# "parent": "sales_order_no",
				# "stock_uom": "uom"
			}
		}
	}, target_doc, postprocess)

	return doc
