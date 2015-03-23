# Copyright (c) 2013, New Indictrans technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class CellMaster(Document):
	# pass
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname(self.zone + '/' + self.church + '/' + 'CELL' + '.####')

	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select zone,church_group,church,pcf,name from `tabSenior Cell Master` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0],
					"church_group" : value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region,church_group,church,pcf,name from `tabSenior Cell Master` where zone='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"church_group" : value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.church_group:
			value = frappe.db.sql("select region,zone,church,pcf,name from `tabSenior Cell Master` where church_group='%s'"%(self.church_group),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.church:
			value = frappe.db.sql("select region,zone,church_group,pcf,name from `tabSenior Cell Master` where church='%s'"%(self.church),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"pcf" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.pcf:
			value = frappe.db.sql("select region,zone,church_group,church,name from `tabSenior Cell Master` where pcf='%s'"%(self.pcf),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"senior_cell" : value[0][4]
				}
			return ret
		elif self.senior_cell:
			value = frappe.db.sql("select region,zone,church_group,church,pcf from `tabSenior Cell Master` where name='%s'"%(self.senior_cell),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3],
					"pcf" : value[0][4]
				}
			return ret

def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabCell Master` where cell_name='%s' and cell_code='%s' and senior_cell='%s'"%(doc.cell_name,doc.cell_code,doc.senior_cell))
		if res:
			frappe.throw(_("Another Cell '{0}' With Cell Name '{1}' and Cell Code '{2}' exist in Senior Cell '{3}'..!").format(res[0][0],doc.cell_name,doc.cell_code,doc.senior_cell))

