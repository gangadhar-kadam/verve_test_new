# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import throw, _, msgprint

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

	# def on_update(self):
	# 	fdate=self.from_date.split(" ")
	# 	f_date=fdate[0]
	# 	tdate=self.to_date.split(" ")
	# 	t_date=tdate[0]
	# 	res=frappe.db.sql("select name from `tabCell Meeting Invitation` where (cell='%s' or church='%s') and from_date like '%s%%' and to_date like '%s%%'"%(self.cell,self.church,f_date,t_date))
	# 	frappe.errprint(res)
	# 	if res:
	# 		frappe.throw(("Cell Meeting Invitation '{0}' is already created for same details on same date '{1}'").format(res[0][0],f_date))
		
def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		fdate=doc.from_date.split(" ")
		f_date=fdate[0]
		frappe.errprint(f_date)
		tdate=doc.to_date.split(" ")
		t_date=tdate[0]
		frappe.errprint(t_date)
		res=frappe.db.sql("select name from `tabCell Meeting Invitation` where (cell='%s' or church='%s') and from_date like '%s%%' and to_date like '%s%%'"%(doc.cell,doc.church,f_date,t_date))
		frappe.errprint(res)
		if res:
			frappe.throw(_("Cell Meeting Invitation '{0}' is already created for same details on same date '{1}'").format(res[0][0],f_date))

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
