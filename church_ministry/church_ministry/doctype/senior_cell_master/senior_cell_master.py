# Copyright (c) 2013, New Indictrans technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class SeniorCellMaster(Document):
	# pass
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname(self.zone + '/' + self.church + '/' + 'SRCELL' + '.####')

	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select zone,church_group,church,name from `tabPCF Master` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0],
					"church_group" : value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region,church_group,church,name from `tabPCF Master` where zone='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"church_group" : value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3]
				}
			return ret
		elif self.church_group:
			value = frappe.db.sql("select region,zone,church,name from `tabPCF Master` where church_group='%s'"%(self.church_group),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church" : value[0][2],
					"pcf" : value[0][3]
				}
			return ret
		elif self.church:
			value = frappe.db.sql("select region,zone,church_group,name from `tabPCF Master` where church='%s'"%(self.church),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"pcf" : value[0][3]
				}
			return ret
		elif self.pcf:
			value = frappe.db.sql("select region,zone,church_group,church from `tabPCF Master` where name='%s'"%(self.pcf),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2],
					"church" : value[0][3]
				}
			return ret



def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabSenior Cell Master` where senior_cell_name='%s' and senior_cell_code='%s' and pcf='%s'"%(doc.senior_cell_name,doc.senior_cell_code,doc.pcf))
		if res:
			frappe.throw(_("Another Senior Cell '{0}' With Senior Cell Name '{1}' and Senior Cell Code '{2}' exist in PCF '{3}'..!").format(res[0][0],doc.senior_cell_name,doc.senior_cell_code,doc.pcf))

