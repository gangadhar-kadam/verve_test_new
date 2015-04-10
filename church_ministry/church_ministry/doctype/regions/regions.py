# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class Regions(Document):
	pass


def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabRegions` where region_name='%s' and region_code='%s'"%(doc.region_name,doc.region_code))
		if res:
			frappe.throw(_("Another Region '{0}' With Region Name '{1}' and Region Code '{2}' exist ..!").format(res[0][0],doc.region_name,doc.region_code))

