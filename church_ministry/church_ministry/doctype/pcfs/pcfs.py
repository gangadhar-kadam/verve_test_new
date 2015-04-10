# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class PCFs(Document):
	# pass
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname(self.church + '/' + 'PCF' + '.####')

	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select zone,church_group,name from `tabChurches` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0],
					"church_group" : value[0][1],
					"church" : value[0][2]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region,church_group,name from `tabChurches` where zone='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"church_group" : value[0][1],
					"church" : value[0][2]
				}
			return ret
		elif self.church_group:
			value = frappe.db.sql("select region,zone,name from `tabChurches` where church_group='%s'"%(self.church_group),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church" : value[0][2]
				}
			return ret
		elif self.church:
			value = frappe.db.sql("select region,zone,church_group from `tabChurches` where name='%s'"%(self.church),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1],
					"church_group" : value[0][2]
				}
			return ret


def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabPCFs` where pcf_name='%s' and pcf_code='%s' and church='%s'"%(doc.pcf_name,doc.pcf_code,doc.church))
		if res:
			frappe.throw(_("Another PCF '{0}' With PCF Name '{1}' and PCF Code '{2}' exist in Church '{3}'..!").format(res[0][0],doc.pcf_name,doc.pcf_code,doc.church))
