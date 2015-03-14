# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, validate_email_add, cint
from frappe import throw, _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe import msgprint, _
import frappe, os, json

class FirstTimeVisitor(Document):
	
	def validate(self):
		if self.date_of_birth and self.date_of_visit and getdate(self.date_of_birth) >= getdate(self.date_of_visit):		
			frappe.throw(_("Date of Visit '{0}' must be greater than Date of Birth '{1}'").format(self.date_of_visit, self.date_of_birth))
		if self.baptisum_status=='Yes':
			if not self.baptism_when or self.baptism_where :
				frappe.throw(_("When and Where is Mandatory if 'Baptisum Status' is 'Yes'..!"))

		if self.email_id:
			if not validate_email_add(self.email_id):
				frappe.throw(_('{0} is not a valid email id').format(self.email_id))


	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select zone,church_group,church,pcf,senior_cell,name from `tabCell Master` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0],
					"church_group": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region,church_group,church,pcf,senior_cell,name from `tabCell Master` where zone='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"church_group": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.church_group:
			value = frappe.db.sql("select region,zone,church,pcf,senior_cell,name from `tabCell Master` where church_group='%s'"%(self.church_group),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.church:
			value = frappe.db.sql("select region,zone,church_group,pcf,senior_cell,name from `tabCell Master` where church='%s'"%(self.church),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.pcf:
			value = frappe.db.sql("select region,zone,church_group,church,senior_cell,name from `tabCell Master` where pcf='%s'"%(self.pcf),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"senior_cell" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.senior_cell:
			value = frappe.db.sql("select region,zone,church_group,church,pcf,name from `tabCell Master` where senior_cell='%s'"%(self.senior_cell),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"pcf" : value[0][4],
					"cell" : value[0][5]
				}
			return ret
		elif self.cell:
			value = frappe.db.sql("select region,zone,church_group,church,pcf,senior_cell from `tabCell Master` where name='%s'"%(self.cell),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"pcf" : value[0][4],
					"senior_cell" : value[0][5]
				}
			return ret


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


@frappe.whitelist()
def set_higher_values(args):
    args = json.loads(args)
    keys = ["region", "zone", "church_group", "church", "pcf", "senior_cell", "name"]
    out = frappe.db.get_all("Cell Master", fields=keys, filters={'name':args['name']})
    if out:
          return out[0]



