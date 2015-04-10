# Copyright (c) 2013, New Indictrans Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import throw, _, msgprint
from frappe.utils import cstr, cint

class FoundationSchoolExams(Document):
	pass


def validate_duplicate(doc,method):
	if doc.get("__islocal"): 
		res=frappe.db.sql("select name from `tabFoundation School Exams` where exam_name='%s' and exam_code='%s' and max_score='%s' and min_score='%s'"%(doc.exam_name,doc.exam_code,doc.max_score,doc.min_score))
		if res:
			frappe.throw(_("Another Foundation School Exam '{0}' With Exam Name '{1}' , Exam Code '{2}', Max Score '{3}' and Min Score '{4}' exist.!").format(res[0][0],doc.exam_name,doc.exam_code,doc.max_score,doc.min_score))
	if doc.min_score<=0 or doc.max_score <=0 :
		frappe.throw(_("Min Score and Max Score must be grater than '0' ..!"))
	if cint(doc.min_score) > cint(doc.max_score):
		frappe.throw(_("Min Score Must be less than or equal to Max Score ..!"))
