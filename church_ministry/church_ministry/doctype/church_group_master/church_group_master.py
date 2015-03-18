# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class ChurchGroupMaster(Document):
	def onload(self):
		frappe.errprint("in server onload")

	def get_region(self):
		frappe.errprint("get region")
		# to auto set region on load if zone is set
		region = frappe.db.sql("""select region from `tabZone`	where name ='%s'""", self.doc.zone)
		frappe.errprint(get_region)
		ret = {
			'region': region and region[0][0] or ''
		}
		return ret

	def set_higher_values(self):
		if self.region:
			value = frappe.db.sql("select name from `tabZone Master` where region='%s'"%(self.region),as_list=1)
			ret={}
			if value:
				ret={
					"zone": value[0][0]
				}
			return ret
		elif self.zone:
			value = frappe.db.sql("select region from `tabZone Master` where name='%s'"%(self.zone),as_list=1)
			ret={}
			if value:
				ret={
					"region": value[0][0]
				}
			return ret


def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabChurch Group Master` where church_group='%s' and church_group_code='%s' and zone='%s'"%(doc.church_group,doc.church_group_code,doc.zone))
		if res:
			frappe.throw(_("Another Church Group '{0}' With Church Group Name '{1}' and Church Group Code '{2}' exist in Zone '{3}'..!").format(res[0][0],doc.church_group,doc.church_group_code,doc.zone))
