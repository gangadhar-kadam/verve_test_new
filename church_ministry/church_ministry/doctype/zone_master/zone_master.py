# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class ZoneMaster(Document):
	pass


def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabZone Master` where (zone_name='%s' or zone_code='%s') and region='%s'"%(doc.zone_name,doc.zone_code,doc.region))
		frappe.errprint(res)
		if res:
			frappe.throw(_("Zone '{0}' already created with same Zone Name '{1}' or Zone Code '{2}' for Region '{3}'..!").format(res[0][0],doc.zone_name,doc.zone_code,doc.region))
