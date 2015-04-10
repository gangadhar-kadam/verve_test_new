# Copyright (c) 2015, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint

class FoundationSchoolGrades(Document):
	pass

def validate_duplicate(doc,method):
	if doc.get("__islocal"):
		res=frappe.db.sql("select name from `tabFoundation School Grades` where grade='%s' and from_score='%s' and to_score='%s'"%(doc.grade,doc.from_score,doc.to_score))
		if res:
			frappe.throw(_("Another FS Grade '{0}' With FS Grade Name '{1}' and From Score '{2}' and To Score '{3}' exist.!").format(res[0][0],doc.grade,doc.from_score,doc.to_score))

