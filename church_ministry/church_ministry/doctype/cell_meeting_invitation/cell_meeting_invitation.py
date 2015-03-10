# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import throw, _, msgprint
import frappe.share
from frappe.utils import cstr,now,add_days,nowdate

class CellMeetingInvitation(Document):
	
	def  load_table(self):
		self.set('invitation_member_details', [])
		if self.cell:
			member_ftv = frappe.db.sql("select name,ftv_name,email_id from `tabFirst Time Visitor` where cell='%s' and approved=0 union select name,member_name,email_id from `tabMember` where cell='%s' "%(self.cell,self.cell))
		elif self.church:
			member_ftv = frappe.db.sql("select name,ftv_name,email_id from `tabFirst Time Visitor` where church='%s' and approved=0 union select name,member_name,email_id from `tabMember` where church='%s'"%(self.church,self.church))
		for d in member_ftv:
			child = self.append('invitation_member_details', {})
			child.member = d[0]
			child.member_name = d[1]
			child.email_id = d[2]

	def on_submit(self):
			#if self.flag=='False':
			event = frappe.get_doc({
				"doctype": "Event",
				"owner": frappe.session.user,
				"subject": "Cell Meeting Invitation",
				"description": "Cell Meeting Invitation",
				"starts_on": add_days(now(), 3),
				"event_type": "Private",
				"ref_type": "Cell Meeting Invitation",
				"ref_name": self.name
			})
			event.insert(ignore_permissions=True)
			for d in self.get('invitation_member_details'):
				if frappe.db.exists("User", d.email_id):
					frappe.share.add("Event", event.name, d.email_id, "read")
		
	def set_higher_values(self):
		if self.church_master:
			value = frappe.db.sql("select region,zone,church_group,pcf,senior_cell,name from `tabCell Master` where church='%s'"%(self.church),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell_master" : value[0][5]
				}
			return ret
		elif self.cell_master:
			value = frappe.db.sql("select region,zone,church_group,church,pcf,senior_cell from `tabCell Master` where name='%s'"%(self.cell),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church_master" : value[0][3],
					"pcf" : value[0][4],
					"senior_cell" : value[0][5]
				}
			return ret


def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		fdate=doc.from_date.split(" ")
		f_date=fdate[0]
		tdate=doc.to_date.split(" ")
		t_date=tdate[0]
		res=frappe.db.sql("select name from `tabCell Meeting Invitation` where (cell='%s' or church='%s') and from_date like '%s%%' and to_date like '%s%%'"%(doc.cell,doc.church,f_date,t_date))
		if res:
			frappe.throw(_("Cell Meeting Invitation '{0}' is already created for same details on same date '{1}'").format(res[0][0],f_date))

		if doc.from_date and doc.to_date:
			if doc.from_date >= doc.to_date:
				frappe.throw(_("To Date should be greater than From Date..!"))

		if len(doc.invitation_member_details)<1:
			frappe.throw(_("Invitation Member table is empty.There should be at least 1 member in invitation list. Please load members in table."))

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
