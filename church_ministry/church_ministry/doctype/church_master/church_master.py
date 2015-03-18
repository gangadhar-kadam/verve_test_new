# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class ChurchMaster(Document):
	# pass
	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select zone,name from `tabGroup Church Master` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0],
					"church_group" : value[0][1]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region,name from `tabGroup Church Master` where zone='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"church_group" : value[0][1]
				}
			return ret
		elif self.church_group:
			value = frappe.db.sql("select region,zone from `tabGroup Church Master` where name='%s'"%(self.church_group),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0],
					"zone": value[0][1]
				}
			return ret


def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabChurch Master` where church_name='%s' and church_group='%s' and church_code='%s'"%(doc.church_name,doc.church_group,doc.church_code))
		if res:
			frappe.throw(_("Another Church '{3}' With Church Name '{0}' and Church Code '{2}'' exist in Church Group '{1}'").format(doc.church_name, doc.church_group,doc.church_code,res[0][0]))
